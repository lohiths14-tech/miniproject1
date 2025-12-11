import { useEffect, useState } from 'react';
import {
    ActivityIndicator,
    FlatList,
    RefreshControl,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import api from '../services/api';

const SubmissionsScreen = () => {
    const [submissions, setSubmissions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    useEffect(() => {
        fetchSubmissions();
    }, []);

    const fetchSubmissions = async () => {
        try {
            const response = await api.getMySubmissions();
            setSubmissions(response.data.submissions || []);
        } catch (error) {
            console.error('Failed to fetch submissions:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const onRefresh = () => {
        setRefreshing(true);
        fetchSubmissions();
    };

    const getGradeColor = (grade) => {
        if (grade >= 90) return '#27ae60';
        if (grade >= 70) return '#3498db';
        if (grade >= 50) return '#f39c12';
        return '#e74c3c';
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'graded': return 'check-circle';
            case 'pending': return 'clock-outline';
            case 'processing': return 'cog';
            default: return 'help-circle-outline';
        }
    };

    const renderSubmission = ({ item }) => (
        <TouchableOpacity style={styles.submissionCard}>
            <View style={styles.cardHeader}>
                <Text style={styles.assignmentTitle}>{item.assignmentTitle || 'Assignment'}</Text>
                <View style={[styles.statusBadge, { backgroundColor: item.status === 'graded' ? '#27ae60' : '#f39c12' }]}>
                    <Icon name={getStatusIcon(item.status)} size={12} color="#fff" />
                    <Text style={styles.statusText}>{item.status || 'pending'}</Text>
                </View>
            </View>

            <View style={styles.cardBody}>
                <View style={styles.infoRow}>
                    <Icon name="code-tags" size={16} color="#666" />
                    <Text style={styles.infoText}>{item.language || 'Unknown'}</Text>
                </View>
                <View style={styles.infoRow}>
                    <Icon name="calendar" size={16} color="#666" />
                    <Text style={styles.infoText}>
                        {new Date(item.createdAt).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                        })}
                    </Text>
                </View>
            </View>

            {item.status === 'graded' && (
                <View style={styles.gradeSection}>
                    <View style={[styles.gradeCircle, { borderColor: getGradeColor(item.grade) }]}>
                        <Text style={[styles.gradeValue, { color: getGradeColor(item.grade) }]}>
                            {item.grade}%
                        </Text>
                    </View>
                    {item.feedback && (
                        <View style={styles.feedbackContainer}>
                            <Text style={styles.feedbackLabel}>Feedback:</Text>
                            <Text style={styles.feedbackText} numberOfLines={2}>
                                {item.feedback}
                            </Text>
                        </View>
                    )}
                </View>
            )}
        </TouchableOpacity>
    );

    if (loading) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#667eea" />
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <FlatList
                data={submissions}
                keyExtractor={(item) => item.id?.toString() || item._id}
                renderItem={renderSubmission}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
                }
                contentContainerStyle={styles.listContent}
                ListEmptyComponent={
                    <View style={styles.emptyContainer}>
                        <Icon name="file-document-outline" size={60} color="#ccc" />
                        <Text style={styles.emptyText}>No submissions yet</Text>
                        <Text style={styles.emptySubtext}>
                            Complete an assignment to see your submissions here
                        </Text>
                    </View>
                }
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    listContent: {
        padding: 15,
    },
    submissionCard: {
        backgroundColor: '#fff',
        borderRadius: 10,
        padding: 15,
        marginBottom: 15,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    cardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 10,
    },
    assignmentTitle: {
        fontSize: 16,
        fontWeight: '600',
        color: '#333',
        flex: 1,
    },
    statusBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 10,
        paddingVertical: 4,
        borderRadius: 12,
    },
    statusText: {
        color: '#fff',
        fontSize: 11,
        fontWeight: '600',
        marginLeft: 4,
        textTransform: 'capitalize',
    },
    cardBody: {
        flexDirection: 'row',
        marginBottom: 10,
    },
    infoRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginRight: 20,
    },
    infoText: {
        marginLeft: 5,
        color: '#666',
        fontSize: 13,
    },
    gradeSection: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingTop: 10,
        borderTopWidth: 1,
        borderTopColor: '#f0f0f0',
    },
    gradeCircle: {
        width: 60,
        height: 60,
        borderRadius: 30,
        borderWidth: 3,
        justifyContent: 'center',
        alignItems: 'center',
    },
    gradeValue: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    feedbackContainer: {
        flex: 1,
        marginLeft: 15,
    },
    feedbackLabel: {
        fontSize: 12,
        color: '#999',
        marginBottom: 4,
    },
    feedbackText: {
        fontSize: 13,
        color: '#555',
        lineHeight: 18,
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingTop: 100,
    },
    emptyText: {
        fontSize: 18,
        color: '#999',
        marginTop: 15,
    },
    emptySubtext: {
        fontSize: 14,
        color: '#bbb',
        marginTop: 5,
        textAlign: 'center',
    },
});

export default SubmissionsScreen;
