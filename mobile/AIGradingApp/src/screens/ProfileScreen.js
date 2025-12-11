import { useEffect, useState } from 'react';
import {
    Alert,
    RefreshControl,
    ScrollView,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import AchievementBadge from '../components/AchievementBadge';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const ProfileScreen = ({ navigation }) => {
    const { user, logout } = useAuth();
    const [achievements, setAchievements] = useState([]);
    const [submissions, setSubmissions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    useEffect(() => {
        fetchProfileData();
    }, []);

    const fetchProfileData = async () => {
        try {
            const [achievementsRes, submissionsRes] = await Promise.all([
                api.getMyAchievements(),
                api.getMySubmissions(),
            ]);
            setAchievements(achievementsRes.data.achievements || []);
            setSubmissions(submissionsRes.data.submissions || []);
        } catch (error) {
            console.error('Failed to fetch profile data:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const onRefresh = () => {
        setRefreshing(true);
        fetchProfileData();
    };

    const handleLogout = () => {
        Alert.alert(
            'Logout',
            'Are you sure you want to logout?',
            [
                { text: 'Cancel', style: 'cancel' },
                { text: 'Logout', style: 'destructive', onPress: logout },
            ]
        );
    };

    const getLevelColor = (level) => {
        const colors = {
            'Beginner': '#95a5a6',
            'Novice': '#3498db',
            'Intermediate': '#27ae60',
            'Advanced': '#9b59b6',
            'Expert': '#f39c12',
            'Master': '#e74c3c',
            'Legend': '#667eea',
        };
        return colors[level] || '#667eea';
    };

    return (
        <ScrollView
            style={styles.container}
            refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }
        >
            <View style={styles.header}>
                <View style={styles.avatarContainer}>
                    <View style={styles.avatar}>
                        <Text style={styles.avatarText}>
                            {user?.username?.charAt(0)?.toUpperCase() || 'U'}
                        </Text>
                    </View>
                    <View style={[styles.levelBadge, { backgroundColor: getLevelColor(user?.level) }]}>
                        <Text style={styles.levelText}>{user?.level || 'Beginner'}</Text>
                    </View>
                </View>
                <Text style={styles.username}>{user?.username || 'Student'}</Text>
                <Text style={styles.email}>{user?.email || ''}</Text>

                <View style={styles.statsRow}>
                    <View style={styles.statItem}>
                        <Text style={styles.statValue}>{user?.points || 0}</Text>
                        <Text style={styles.statLabel}>Points</Text>
                    </View>
                    <View style={styles.statDivider} />
                    <View style={styles.statItem}>
                        <Text style={styles.statValue}>{submissions.length}</Text>
                        <Text style={styles.statLabel}>Submissions</Text>
                    </View>
                    <View style={styles.statDivider} />
                    <View style={styles.statItem}>
                        <Text style={styles.statValue}>{achievements.length}</Text>
                        <Text style={styles.statLabel}>Badges</Text>
                    </View>
                </View>
            </View>

            <View style={styles.section}>
                <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Achievements</Text>
                    <TouchableOpacity>
                        <Text style={styles.seeAll}>See All</Text>
                    </TouchableOpacity>
                </View>
                {achievements.length > 0 ? (
                    <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                        {achievements.slice(0, 10).map((achievement, index) => (
                            <AchievementBadge key={index} achievement={achievement} />
                        ))}
                    </ScrollView>
                ) : (
                    <Text style={styles.emptyText}>No achievements yet. Keep coding!</Text>
                )}
            </View>

            <View style={styles.section}>
                <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Recent Submissions</Text>
                    <TouchableOpacity onPress={() => navigation.navigate('Submissions')}>
                        <Text style={styles.seeAll}>See All</Text>
                    </TouchableOpacity>
                </View>
                {submissions.slice(0, 5).map((submission, index) => (
                    <View key={index} style={styles.submissionItem}>
                        <View style={styles.submissionInfo}>
                            <Text style={styles.submissionTitle}>{submission.assignmentTitle || 'Assignment'}</Text>
                            <Text style={styles.submissionDate}>
                                {new Date(submission.createdAt).toLocaleDateString()}
                            </Text>
                        </View>
                        <View style={[styles.gradeBadge, { backgroundColor: submission.grade >= 70 ? '#27ae60' : '#e74c3c' }]}>
                            <Text style={styles.gradeText}>{submission.grade}%</Text>
                        </View>
                    </View>
                ))}
                {submissions.length === 0 && (
                    <Text style={styles.emptyText}>No submissions yet.</Text>
                )}
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Settings</Text>
                <TouchableOpacity style={styles.settingItem}>
                    <Icon name="account-edit" size={24} color="#667eea" />
                    <Text style={styles.settingText}>Edit Profile</Text>
                    <Icon name="chevron-right" size={24} color="#ccc" />
                </TouchableOpacity>
                <TouchableOpacity style={styles.settingItem}>
                    <Icon name="bell-outline" size={24} color="#667eea" />
                    <Text style={styles.settingText}>Notifications</Text>
                    <Icon name="chevron-right" size={24} color="#ccc" />
                </TouchableOpacity>
                <TouchableOpacity style={styles.settingItem}>
                    <Icon name="shield-check" size={24} color="#667eea" />
                    <Text style={styles.settingText}>Privacy</Text>
                    <Icon name="chevron-right" size={24} color="#ccc" />
                </TouchableOpacity>
                <TouchableOpacity style={styles.settingItem}>
                    <Icon name="help-circle-outline" size={24} color="#667eea" />
                    <Text style={styles.settingText}>Help & Support</Text>
                    <Icon name="chevron-right" size={24} color="#ccc" />
                </TouchableOpacity>
            </View>

            <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
                <Icon name="logout" size={20} color="#e74c3c" />
                <Text style={styles.logoutText}>Logout</Text>
            </TouchableOpacity>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    header: {
        backgroundColor: '#667eea',
        alignItems: 'center',
        paddingVertical: 30,
        paddingHorizontal: 20,
    },
    avatarContainer: {
        position: 'relative',
    },
    avatar: {
        width: 100,
        height: 100,
        borderRadius: 50,
        backgroundColor: '#fff',
        justifyContent: 'center',
        alignItems: 'center',
    },
    avatarText: {
        fontSize: 40,
        fontWeight: 'bold',
        color: '#667eea',
    },
    levelBadge: {
        position: 'absolute',
        bottom: 0,
        right: -10,
        paddingHorizontal: 10,
        paddingVertical: 4,
        borderRadius: 10,
    },
    levelText: {
        color: '#fff',
        fontSize: 10,
        fontWeight: 'bold',
    },
    username: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#fff',
        marginTop: 15,
    },
    email: {
        fontSize: 14,
        color: 'rgba(255,255,255,0.8)',
        marginTop: 5,
    },
    statsRow: {
        flexDirection: 'row',
        marginTop: 20,
        backgroundColor: 'rgba(255,255,255,0.1)',
        borderRadius: 10,
        padding: 15,
    },
    statItem: {
        flex: 1,
        alignItems: 'center',
    },
    statValue: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#fff',
    },
    statLabel: {
        fontSize: 12,
        color: 'rgba(255,255,255,0.8)',
        marginTop: 4,
    },
    statDivider: {
        width: 1,
        backgroundColor: 'rgba(255,255,255,0.3)',
    },
    section: {
        backgroundColor: '#fff',
        marginTop: 10,
        padding: 20,
    },
    sectionHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 15,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
    },
    seeAll: {
        color: '#667eea',
        fontSize: 14,
    },
    emptyText: {
        color: '#999',
        fontSize: 14,
        textAlign: 'center',
        paddingVertical: 20,
    },
    submissionItem: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#f0f0f0',
    },
    submissionInfo: {
        flex: 1,
    },
    submissionTitle: {
        fontSize: 15,
        color: '#333',
        fontWeight: '500',
    },
    submissionDate: {
        fontSize: 12,
        color: '#999',
        marginTop: 4,
    },
    gradeBadge: {
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 15,
    },
    gradeText: {
        color: '#fff',
        fontSize: 13,
        fontWeight: 'bold',
    },
    settingItem: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 15,
        borderBottomWidth: 1,
        borderBottomColor: '#f0f0f0',
    },
    settingText: {
        flex: 1,
        marginLeft: 15,
        fontSize: 16,
        color: '#333',
    },
    logoutButton: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#fff',
        margin: 20,
        padding: 15,
        borderRadius: 10,
        borderWidth: 1,
        borderColor: '#e74c3c',
    },
    logoutText: {
        color: '#e74c3c',
        fontSize: 16,
        fontWeight: '600',
        marginLeft: 10,
    },
});

export default ProfileScreen;
