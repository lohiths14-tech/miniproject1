import subprocess
import tempfile
import os
import time
import signal
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
from threading import Timer

def compile_and_run_code(code, language, test_input='', timeout=10):
    """
    Compile and run code safely with timeout and resource limits
    
    Args:
        code (str): Source code to execute
        language (str): Programming language
        test_input (str): Input for the program
        timeout (int): Timeout in seconds
    
    Returns:
        dict: Execution result with output, errors, and stats
    """
    result = {
        'success': False,
        'output': '',
        'error': '',
        'execution_time': 0,
        'memory_usage': 0,
        'compile_time': 0
    }
    
    try:
        language = language.lower()
        
        if language == 'python':
            return execute_python(code, test_input, timeout, result)
        elif language == 'java':
            return execute_java(code, test_input, timeout, result)
        elif language in ['cpp', 'c++']:
            return execute_cpp(code, test_input, timeout, result)
        elif language == 'c':
            return execute_c(code, test_input, timeout, result)
        elif language == 'javascript':
            return execute_javascript(code, test_input, timeout, result)
        else:
            result['error'] = f'Unsupported language: {language}'
            return result
            
    except Exception as e:
        result['error'] = f'Execution failed: {str(e)}'
        return result

def execute_python(code, test_input, timeout, result):
    """Execute Python code"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            start_time = time.time()
            
            # Create process with resource limits
            process = subprocess.Popen(
                ['python', f.name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=set_resource_limits if os.name != 'nt' else None
            )
            
            try:
                # Monitor memory usage
                if PSUTIL_AVAILABLE:
                    psutil_process = psutil.Process(process.pid)
                    max_memory = 0
                else:
                    max_memory = 0
                
                # Use timeout
                output, error = process.communicate(input=test_input, timeout=timeout)
                
                execution_time = time.time() - start_time
                
                try:
                    if PSUTIL_AVAILABLE:
                        memory_info = psutil_process.memory_info()
                        max_memory = memory_info.rss / 1024 / 1024  # MB
                    else:
                        max_memory = 0
                except:
                    max_memory = 0
                
                result['execution_time'] = execution_time
                result['memory_usage'] = max_memory
                
                if process.returncode == 0:
                    result['success'] = True
                    result['output'] = output
                else:
                    result['error'] = error
                
            except subprocess.TimeoutExpired:
                process.kill()
                result['error'] = f'Execution timeout ({timeout} seconds)'
            except Exception as e:
                process.kill()
                result['error'] = str(e)
                
    except Exception as e:
        result['error'] = str(e)
    finally:
        try:
            os.unlink(f.name)
        except:
            pass
    
    return result

def execute_java(code, test_input, timeout, result):
    """Execute Java code"""
    try:
        # Extract class name
        class_name = 'Main'
        import re
        match = re.search(r'public class\s+(\w+)', code)
        if match:
            class_name = match.group(1)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            java_file = os.path.join(temp_dir, f'{class_name}.java')
            
            with open(java_file, 'w') as f:
                f.write(code)
            
            # Compile
            compile_start = time.time()
            compile_process = subprocess.run(
                ['javac', java_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            result['compile_time'] = time.time() - compile_start
            
            if compile_process.returncode != 0:
                result['error'] = f'Compilation error: {compile_process.stderr}'
                return result
            
            # Run
            start_time = time.time()
            run_process = subprocess.Popen(
                ['java', '-cp', temp_dir, class_name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=temp_dir,
                preexec_fn=set_resource_limits if os.name != 'nt' else None
            )
            
            try:
                output, error = run_process.communicate(input=test_input, timeout=timeout)
                execution_time = time.time() - start_time
                
                result['execution_time'] = execution_time
                
                if run_process.returncode == 0:
                    result['success'] = True
                    result['output'] = output
                else:
                    result['error'] = error
                    
            except subprocess.TimeoutExpired:
                run_process.kill()
                result['error'] = f'Execution timeout ({timeout} seconds)'
                
    except Exception as e:
        result['error'] = str(e)
    
    return result

def execute_cpp(code, test_input, timeout, result):
    """Execute C++ code"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            cpp_file = os.path.join(temp_dir, 'main.cpp')
            exe_file = os.path.join(temp_dir, 'main.exe' if os.name == 'nt' else 'main')
            
            with open(cpp_file, 'w') as f:
                f.write(code)
            
            # Compile
            compile_start = time.time()
            compile_cmd = ['g++', '-o', exe_file, cpp_file, '-std=c++17']
            compile_process = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            result['compile_time'] = time.time() - compile_start
            
            if compile_process.returncode != 0:
                result['error'] = f'Compilation error: {compile_process.stderr}'
                return result
            
            # Run
            start_time = time.time()
            run_process = subprocess.Popen(
                [exe_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=set_resource_limits if os.name != 'nt' else None
            )
            
            try:
                output, error = run_process.communicate(input=test_input, timeout=timeout)
                execution_time = time.time() - start_time
                
                result['execution_time'] = execution_time
                
                if run_process.returncode == 0:
                    result['success'] = True
                    result['output'] = output
                else:
                    result['error'] = error
                    
            except subprocess.TimeoutExpired:
                run_process.kill()
                result['error'] = f'Execution timeout ({timeout} seconds)'
                
    except Exception as e:
        result['error'] = str(e)
    
    return result

def execute_c(code, test_input, timeout, result):
    """Execute C code"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            c_file = os.path.join(temp_dir, 'main.c')
            exe_file = os.path.join(temp_dir, 'main.exe' if os.name == 'nt' else 'main')
            
            with open(c_file, 'w') as f:
                f.write(code)
            
            # Compile
            compile_start = time.time()
            compile_cmd = ['gcc', '-o', exe_file, c_file]
            compile_process = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            result['compile_time'] = time.time() - compile_start
            
            if compile_process.returncode != 0:
                result['error'] = f'Compilation error: {compile_process.stderr}'
                return result
            
            # Run
            start_time = time.time()
            run_process = subprocess.Popen(
                [exe_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=set_resource_limits if os.name != 'nt' else None
            )
            
            try:
                output, error = run_process.communicate(input=test_input, timeout=timeout)
                execution_time = time.time() - start_time
                
                result['execution_time'] = execution_time
                
                if run_process.returncode == 0:
                    result['success'] = True
                    result['output'] = output
                else:
                    result['error'] = error
                    
            except subprocess.TimeoutExpired:
                run_process.kill()
                result['error'] = f'Execution timeout ({timeout} seconds)'
                
    except Exception as e:
        result['error'] = str(e)
    
    return result

def execute_javascript(code, test_input, timeout, result):
    """Execute JavaScript code using Node.js"""
    try:
        # Wrap code to handle input
        wrapped_code = f"""
const readline = require('readline');
const rl = readline.createInterface({{
    input: process.stdin,
    output: process.stdout
}});

let inputLines = `{test_input}`.split('\\n');
let currentLine = 0;

// Mock input function
function input() {{
    return inputLines[currentLine++] || '';
}}

// Your code here
{code}

rl.close();
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(wrapped_code)
            f.flush()
            
            start_time = time.time()
            
            process = subprocess.Popen(
                ['node', f.name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=set_resource_limits if os.name != 'nt' else None
            )
            
            try:
                output, error = process.communicate(timeout=timeout)
                execution_time = time.time() - start_time
                
                result['execution_time'] = execution_time
                
                if process.returncode == 0:
                    result['success'] = True
                    result['output'] = output
                else:
                    result['error'] = error
                    
            except subprocess.TimeoutExpired:
                process.kill()
                result['error'] = f'Execution timeout ({timeout} seconds)'
                
    except Exception as e:
        result['error'] = str(e)
    finally:
        try:
            os.unlink(f.name)
        except:
            pass
    
    return result

def set_resource_limits():
    """Set resource limits for subprocess (Unix only)"""
    if os.name != 'nt':  # Not Windows
        try:
            import resource
            
            # Limit CPU time to 10 seconds
            resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
            
            # Limit memory to 128MB
            resource.setrlimit(resource.RLIMIT_AS, (128 * 1024 * 1024, 128 * 1024 * 1024))
            
            # Limit number of processes
            resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
        except ImportError:
            pass  # resource module not available

def check_syntax(code, language):
    """Check syntax without executing the code"""
    try:
        language = language.lower()
        
        if language == 'python':
            try:
                compile(code, '<string>', 'exec')
                return {'valid': True, 'error': None}
            except SyntaxError as e:
                return {'valid': False, 'error': str(e)}
        
        elif language == 'java':
            # Basic Java syntax check (simplified)
            if 'public class' not in code:
                return {'valid': False, 'error': 'No public class found'}
            
            # More comprehensive check would require actual compilation
            return {'valid': True, 'error': None}
        
        elif language in ['cpp', 'c++', 'c']:
            # Basic C/C++ syntax check (simplified)
            if '#include' not in code and 'int main' not in code:
                return {'valid': False, 'error': 'No main function found'}
            
            return {'valid': True, 'error': None}
        
        else:
            return {'valid': False, 'error': f'Syntax check not supported for {language}'}
            
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def get_supported_languages():
    """Get list of supported programming languages"""
    return [
        {'name': 'Python', 'value': 'python', 'extension': '.py'},
        {'name': 'Java', 'value': 'java', 'extension': '.java'},
        {'name': 'C++', 'value': 'cpp', 'extension': '.cpp'},
        {'name': 'C', 'value': 'c', 'extension': '.c'},
        {'name': 'JavaScript', 'value': 'javascript', 'extension': '.js'}
    ]