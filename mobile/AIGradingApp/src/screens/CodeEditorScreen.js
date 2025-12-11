import { useState } from 'react';
import {
    ActivityIndicator,
    Alert,
    KeyboardAvoidingView,
    Platform,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import api from '../services/api';

const LANGUAGES = [
    { id: 'python', name: 'Python', icon: 'language-python' },
    { id: 'javascript', name: 'JavaScript', icon: 'language-javascript' },
    { id: 'java', name: 'Java', icon: 'language-java' },
    { id: 'cpp', name: 'C++', icon: 'language-cpp' },
    { id: 'c', name: 'C', icon: 'language-c' },
];

const CodeEditorScreen = ({ route, navigation }) => {
    const { assignment } = route.params;
    const [code, setCode] = useState('');
    const [language, setLanguage] = useState('python');
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async () => {
        if (!code.trim()) {
            Alert.alert('Error', 'Please enter your code before submitting.');
            return;
        }

        Alert.alert(
            'Submit Code',
            'Are you sure you want to submit your code for grading?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Submit',
                    onPress: async () => {
                        setSubmitting(true);
                        try {
                            const response = await api.submitCode(
                                assignment.id || assignment._id,
                                code,
                                language
                            );
                            Alert.alert(
                                'Success',
                                'Your code has been submitted for grading!',
                                [{ text: 'OK', onPress: () => navigation.goBack() }]
                            );
                        } catch (error) {
                            Alert.alert(
                                'Error',
                                error.response?.data?.message || 'Failed to submit code'
                            );
                        } finally {
                            setSubmitting(false);
                        }
                    },
                },
            ]
        );
    };

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
            <View style={styles.header}>
                <Text style={styles.assignmentTitle} numberOfLines={1}>
                    {assignment.title}
                </Text>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.languageSelector}>
                    {LANGUAGES.map((lang) => (
                        <TouchableOpacity
                            key={lang.id}
                            style={[styles.languageButton, language === lang.id && styles.languageButtonActive]}
                            onPress={() => setLanguage(lang.id)}
                        >
                            <Icon
                                name={lang.icon}
                                size={20}
                                color={language === lang.id ? '#fff' : '#667eea'}
                            />
                            <Text style={[styles.languageText, language === lang.id && styles.languageTextActive]}>
                                {lang.name}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>
            </View>

            <View style={styles.editorContainer}>
                <View style={styles.lineNumbers}>
                    {code.split('\n').map((_, index) => (
                        <Text key={index} style={styles.lineNumber}>
                            {index + 1}
                        </Text>
                    ))}
                    {code.split('\n').length === 0 && <Text style={styles.lineNumber}>1</Text>}
                </View>
                <TextInput
                    style={styles.codeInput}
                    multiline
                    value={code}
                    onChangeText={setCode}
                    placeholder="Write your code here..."
                    placeholderTextColor="#999"
                    autoCapitalize="none"
                    autoCorrect={false}
                    spellCheck={false}
                    textAlignVertical="top"
                />
            </View>

            <View style={styles.footer}>
                <View style={styles.statsRow}>
                    <Text style={styles.statText}>Lines: {code.split('\n').length}</Text>
                    <Text style={styles.statText}>Chars: {code.length}</Text>
                </View>
                <TouchableOpacity
                    style={[styles.submitButton, submitting && styles.submitButtonDisabled]}
                    onPress={handleSubmit}
                    disabled={submitting}
                >
                    {submitting ? (
                        <ActivityIndicator color="#fff" />
                    ) : (
                        <>
                            <Icon name="send" size={20} color="#fff" />
                            <Text style={styles.submitButtonText}>Submit</Text>
                        </>
                    )}
                </TouchableOpacity>
            </View>
        </KeyboardAvoidingView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#1e1e1e',
    },
    header: {
        backgroundColor: '#2d2d2d',
        padding: 15,
    },
    assignmentTitle: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 10,
    },
    languageSelector: {
        flexDirection: 'row',
    },
    languageButton: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 12,
        paddingVertical: 8,
        borderRadius: 20,
        backgroundColor: '#3d3d3d',
        marginRight: 10,
    },
    languageButtonActive: {
        backgroundColor: '#667eea',
    },
    languageText: {
        color: '#667eea',
        marginLeft: 5,
        fontSize: 13,
    },
    languageTextActive: {
        color: '#fff',
    },
    editorContainer: {
        flex: 1,
        flexDirection: 'row',
    },
    lineNumbers: {
        backgroundColor: '#252526',
        paddingVertical: 10,
        paddingHorizontal: 10,
        alignItems: 'flex-end',
    },
    lineNumber: {
        color: '#858585',
        fontSize: 14,
        fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
        lineHeight: 20,
    },
    codeInput: {
        flex: 1,
        backgroundColor: '#1e1e1e',
        color: '#d4d4d4',
        fontSize: 14,
        fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
        padding: 10,
        lineHeight: 20,
    },
    footer: {
        backgroundColor: '#2d2d2d',
        padding: 15,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    statsRow: {
        flexDirection: 'row',
    },
    statText: {
        color: '#858585',
        fontSize: 12,
        marginRight: 15,
    },
    submitButton: {
        flexDirection: 'row',
        backgroundColor: '#667eea',
        paddingHorizontal: 20,
        paddingVertical: 10,
        borderRadius: 20,
        alignItems: 'center',
    },
    submitButtonDisabled: {
        backgroundColor: '#555',
    },
    submitButtonText: {
        color: '#fff',
        fontWeight: '600',
        marginLeft: 8,
    },
});

export default CodeEditorScreen;
