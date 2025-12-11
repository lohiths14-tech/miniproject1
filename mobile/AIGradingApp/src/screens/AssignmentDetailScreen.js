import { useState } from 'react';
import {
    ScrollView,
    Text,
    TouchableOpacity,
    View
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const AssignmentDetailScreen = ({ route, navigation }) => {
    const { assignment } = route.params;
    const [submitting, setSubmitting] = useState(false);

    const formatDate = (dateString) => {
        if (!dateString) return 'No due date';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'graded': return '#27ae60';
            case 'submitted': return '#3498db';
            case 'pending': return '#f39c12';
            default: return '#999';
        }
    };

    const handleStartCoding = () => {
        navigation.navigate('CodeEditor', { assignment });
    };

    const isOverdue = () => {
        if (!assignment.dueDate) return false;
        return new Date(assignment.dueDate) < new Date();
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <View style={styles.titleRow}>
                    <Text style={styles.title}>{assignment.title}</Text>
                    <View style={[styles.statusBadge, { backgroundColor: getStatusColor(assignment.status) }]}>
                        <Text style={styles.statusText}>{assignment.status || 'pending'}</Text>
                    </View>
                </View>

                <View style={styles.metaRow}>
                    <View style={styles.metaItem}>
                        <Icon name="calendar" size={16} color="#666" />
                        <Text style={[styles.metaText, isOverdue() && styles.overdueText]}>
                            {formatDate(assignment.dueDate)}
                        </Text>
                    </View>
                    <View style={styles.metaItem}>
                        <Icon name="star" size={16} color="#f39c12" />
                        <Text style={styles.metaText}>{assignment.maxPoints || 100} points</Text>
                    </View>
                </View>
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Description</Text>
                <Text style={styles.description}>
                    {assignment.description || 'No description provided.'}
                </Text>
            </View>

            {assignment.requirements && (
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Requirements</Text>
                    {assignment.requirements.map((req, index) => (
                        <View key={index} style={styles.requirementItem}>
                            <Icon name="checkbox-blank-circle" size={8} color="#667eea" />
                            <Text style={styles.requirementText}>{req}</Text>
                        </View>
                    ))}
                </View>
            )}

            {assignment.languages && (
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Supported Languages</Text>
                    <View style={styles.languagesRow}>
                        {assignment.languages.map((lang, index) => (
                            <View key={index} style={styles.languageTag}>
                                <Text style={styles.languageText}>{lang}</Text>
                            </View>
                        ))}
                    </View>
                </View>
            )}

            {assignment.status === 'graded' && assignment.grade && (
                <View style={styles.gradeSection}>
                    <Text style={styles.sectionTitle}>Your Grade</Text>
                    <View style={styles.gradeCard}>
                        <Text style={styles.gradeValue}>{assignment.grade}%</Text>
                        <Text style={styles.gradeLabel}>Score</Text>
                    </View>
                    {assignment.feedback && (
                        <View style={styles.feedbackCard}>
                            <Text style={styles.feedbackTitle}>Feedback</Text>
                            <Text style={styles.feedbackText}>{assignment.feedback}</Text>
                        </View>
                    )}
                </View>
            )}

            {assignment.status !== 'graded' && (
                <TouchableOpacity
                    style={[styles.submitButton, isOverdue() && styles.submitButtonDisabled]}
                    onPress={handleStartCoding}
                    disabled={isOverdue()}
                >
                    <Icon name="code-tags" size={24} color="#fff" />
                    <Text style={styles.submitButtonText}>
                        {assignment.status === 'submitted' ? 'Edit Submission' : 'Start Coding'}
                    </Text>
                </TouchableOpacity>
            )}

            {isOverdue() && assignment.status !== 'graded' && (
                <Text style={styles.overdueWarning}>
                    This assignment is past due and can no longer be submitted.
                </Text>
            )}
        </ScrollView>
    );
};


const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    header: {
        backgroundColor: '#fff',
        padding: 20,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
    },
    titleRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
    },
    title: {
        fontSize: 22,
        fontWeight: 'bold',
        color: '#333',
        flex: 1,
        marginRight: 10,
    },
    statusBadge: {
        paddingHorizontal: 12,
        paddingVertical: 4,
        borderRadius: 12,
    },
    statusText: {
        color: '#fff',
        fontSize: 12,
        fontWeight: '600',
        textTransform: 'capitalize',
    },
    metaRow: {
        flexDirection: 'row',
        marginTop: 15,
    },
    metaItem: {
        flexDirection: 'row',
        alignItems: 'center',
        marginRight: 20,
    },
    metaText: {
        marginLeft: 5,
        color: '#666',
        fontSize: 14,
    },
    overdueText: {
        color: '#e74c3c',
    },
    section: {
        backgroundColor: '#fff',
        padding: 20,
        marginTop: 10,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 10,
    },
    description: {
        fontSize: 15,
        color: '#555',
        lineHeight: 22,
    },
    requirementItem: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 8,
    },
    requirementText: {
        marginLeft: 10,
        fontSize: 14,
        color: '#555',
    },
    languagesRow: {
        flexDirection: 'row',
        flexWrap: 'wrap',
    },
    languageTag: {
        backgroundColor: '#e8f4fd',
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 15,
        marginRight: 8,
        marginBottom: 8,
    },
    languageText: {
        color: '#3498db',
        fontSize: 13,
    },
    gradeSection: {
        backgroundColor: '#fff',
        padding: 20,
        marginTop: 10,
    },
    gradeCard: {
        backgroundColor: '#e8f8f5',
        padding: 20,
        borderRadius: 10,
        alignItems: 'center',
    },
    gradeValue: {
        fontSize: 48,
        fontWeight: 'bold',
        color: '#27ae60',
    },
    gradeLabel: {
        fontSize: 14,
        color: '#666',
        marginTop: 5,
    },
    feedbackCard: {
        backgroundColor: '#f8f9fa',
        padding: 15,
        borderRadius: 10,
        marginTop: 15,
    },
    feedbackTitle: {
        fontSize: 14,
        fontWeight: '600',
        color: '#333',
        marginBottom: 8,
    },
    feedbackText: {
        fontSize: 14,
        color: '#555',
        lineHeight: 20,
    },
    submitButton: {
        flexDirection: 'row',
        backgroundColor: '#667eea',
        margin: 20,
        padding: 15,
        borderRadius: 10,
        justifyContent: 'center',
        alignItems: 'center',
    },
    submitButtonDisabled: {
        backgroundColor: '#ccc',
    },
    submitButtonText: {
        color: '#fff',
        fontSize: 18,
        fontWeight: 'bold',
        marginLeft: 10,
    },
    overdueWarning: {
        textAlign: 'center',
        color: '#e74c3c',
        fontSize: 14,
        marginBottom: 20,
        paddingHorizontal: 20,
    },
});

export default AssignmentDetailScreen;
