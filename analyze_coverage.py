import json

# Load coverage data
with open('coverage.json', 'r') as f:
    data = json.load(f)

# Extract service coverage
services = {k: v['summary'] for k, v in data['files'].items() if k.startswith('services\\')}

# Define critical services
critical_services = ['ai_grading_service', 'plagiarism_service', 'gamification_service']

print('=' * 80)
print('SERVICE COVERAGE REPORT')
print('=' * 80)
print()

print('CRITICAL SERVICES (Target: >= 95% coverage):')
print('-' * 80)
critical_results = []
for k, v in services.items():
    if any(c in k for c in critical_services):
        service_name = k.split('\\')[-1]
        coverage = v['percent_covered']
        status = '✓' if coverage >= 95 else '✗'
        print(f'{status} {service_name:45} {coverage:6.2f}%')
        critical_results.append((service_name, coverage))

print()
print('OTHER SERVICES (Target: >= 85% coverage):')
print('-' * 80)
other_results = []
for k, v in services.items():
    if not any(c in k for c in critical_services):
        service_name = k.split('\\')[-1]
        coverage = v['percent_covered']
        status = '✓' if coverage >= 85 else '✗'
        print(f'{status} {service_name:45} {coverage:6.2f}%')
        other_results.append((service_name, coverage))

# Calculate overall coverage
total_stmts = sum(v['num_statements'] for v in services.values())
covered_stmts = sum(v['covered_lines'] for v in services.values())
overall_coverage = (covered_stmts / total_stmts * 100) if total_stmts > 0 else 0

print()
print('=' * 80)
print(f'OVERALL SERVICES COVERAGE: {overall_coverage:.2f}%')
print(f'Target: 85%+ overall')
print(f'Status: {"✓ PASS" if overall_coverage >= 85 else "✗ FAIL"}')
print('=' * 80)
print()

# Summary
critical_pass = sum(1 for _, cov in critical_results if cov >= 95)
other_pass = sum(1 for _, cov in other_results if cov >= 85)

print('SUMMARY:')
print(f'  Critical services passing (>= 95%): {critical_pass}/{len(critical_results)}')
print(f'  Other services passing (>= 85%):    {other_pass}/{len(other_results)}')
print(f'  Overall coverage:                   {overall_coverage:.2f}%')
print()

if overall_coverage >= 85 and critical_pass == len(critical_results):
    print('✓ ALL TARGETS MET!')
else:
    print('✗ TARGETS NOT MET - More testing needed')
    print()
    print('Services needing improvement:')
    for name, cov in critical_results:
        if cov < 95:
            print(f'  - {name}: {cov:.2f}% (need {95-cov:.2f}% more)')
    for name, cov in other_results:
        if cov < 85:
            print(f'  - {name}: {cov:.2f}% (need {85-cov:.2f}% more)')
