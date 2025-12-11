import { useEffect, useState } from 'react';
import {
    RefreshControl,
    ScrollView,
    Text,
    TouchableOpacity,
    View
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import StatsCard from '../components/StatsCard';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const DashboardScreen = ({ navigation }) => {
    const { user } = useAuth();
    const [dashboardData, setDashboardData] = useState(null);
    const [refreshing, setRefreshing] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const response = await api.getDashboardData();
            setDashboardData(response.data);
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const onRefresh = () => {
        setRefreshing(true);
        fetchDashboardData();
    };

    const stats = dashboardData || {
        totalSubmissions: 0,
        averageGrade: 0,
        points: 0,
        level: 'Beginner',
        streak: 0,
        pendingAssignments: 0,
    };

    return (
        <ScrollView
            style={styles.container}
            refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }
        >
            <View style={styles.header}>
                <Text style={styles.greeting}>Welcome back,</Text>
                <Text style={styles.username}>{user?.username || 'Student'}</Text>
            </View>

            <View style={styles.statsGrid}>
                <StatsCard
                    icon="file-document-outline"
                    title="Submissions"
                    value={stats.totalSubmissions}
                    color="#667eea"
                />
                <StatsCard
                    icon="chart-line"
                    title="Avg Grade"
                    value={`${stats.averageGrade}%`}
                    color="#27ae60"
                />
                <StatsCard
                    icon="star"
                    title="Points"
                    value={stats.points}
                    color="#f39c12"
                />
                <StatsCard
                    icon="trophy"
                    title="Level"
                    value={stats.level}
                    color="#9b59b6"
                />
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Quick Actions</Text>
                <View style={styles.actionsGrid}>
                    <TouchableOpacity
                        style={styles.actionButton}
                        onPress={() => navigation.navigate('Assignments')}
                    >
                        <Icon name="book-open-page-variant" size={30} color="#667eea" />
                        <Text style={styles.actionText}>Assignments</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={styles.actionButton}
                        onPress={() => navigation.navigate('Submissions')}
                    >
                        <Icon name="history" size={30} color="#27ae60" />
                        <Text style={styles.actionText}>History</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={styles.actionButton}
                        onPress={() => navigation.navigate('Leaderboard')}
                    >
                        <Icon name="podium" size={30} color="#f39c12" />
                        <Text style={styles.actionText}>Leaderboard</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={styles.actionButton}
                        onPress={() => navigation.navigate('Profile')}
                    >
                        <Icon name="account-circle" size={30} color="#9b59b6" />
                        <Text style={styles.actionText}>Profile</Text>
                    </TouchableOpacity>
                </View>
            </View>

            {stats.pendingAssignments > 0 && (
                <View style={styles.alertCard}>
                    <Icon name="alert-circle" size={24} color="#e74c3c" />
                    <Text style={styles.alertText}>
                        You have {stats.pendingAssignments} pending assignment(s)
                    </Text>
                </View>
            )}

            {stats.streak > 0 && (
                <View style={styles.streakCard}>
                    <Icon name="fire" size={24} color="#f39c12" />
                    <Text style={styles.streakText}>
                        {stats.streak} day streak! Keep it up!
                    </Text>
                </View>
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
        padding: 20,
        backgroundColor: '#667eea',
    },
    greeting: {
        fontSize: 16,
        color: 'rgba(255,255,255,0.8)',
    },
    username: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#fff',
    },
    statsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        padding: 10,
        justifyContent: 'space-between',
    },
    section: {
        padding: 20,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 15,
    },
    actionsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
    },
    actionButton: {
        width: '48%',
        backgroundColor: '#fff',
        borderRadius: 10,
        padding: 20,
        alignItems: 'center',
        marginBottom: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    actionText: {
        marginTop: 10,
        fontSize: 14,
        color: '#333',
        fontWeight: '500',
    },
    alertCard: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#fdeaea',
        margin: 20,
        marginTop: 0,
        padding: 15,
        borderRadius: 10,
        borderLeftWidth: 4,
        borderLeftColor: '#e74c3c',
    },
    alertText: {
        marginLeft: 10,
        color: '#e74c3c',
        fontSize: 14,
        flex: 1,
    },
    streakCard: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#fef9e7',
        margin: 20,
        marginTop: 0,
        padding: 15,
        borderRadius: 10,
        borderLeftWidth: 4,
        borderLeftColor: '#f39c12',
    },
    streakText: {
        marginLeft: 10,
        color: '#f39c12',
        fontSize: 14,
        fontWeight: '500',
    },
});

export default DashboardScreen;
