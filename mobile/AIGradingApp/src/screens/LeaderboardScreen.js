import { useEffect, useState } from 'react';
import {
    ActivityIndicator,
    FlatList,
    RefreshControl,
    Text,
    View
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import LeaderboardItem from '../components/LeaderboardItem';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const LeaderboardScreen = () => {
    const { user } = useAuth();
    const [leaderboard, setLeaderboard] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [timeFilter, setTimeFilter] = useState('all'); // all, weekly, monthly

    useEffect(() => {
        fetchLeaderboard();
    }, [timeFilter]);

    const fetchLeaderboard = async () => {
        try {
            const response = await api.getLeaderboard();
            setLeaderboard(response.data.leaderboard || []);
        } catch (error) {
            console.error('Failed to fetch leaderboard:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const onRefresh = () => {
        setRefreshing(true);
        fetchLeaderboard();
    };

    const renderHeader = () => (
        <View style={styles.headerContainer}>
            <View style={styles.filterRow}>
                {['all', 'weekly', 'monthly'].map((filter) => (
                    <Text
                        key={filter}
                        style={[styles.filterTab, timeFilter === filter && styles.filterTabActive]}
                        onPress={() => setTimeFilter(filter)}
                    >
                        {filter === 'all' ? 'All Time' : filter.charAt(0).toUpperCase() + filter.slice(1)}
                    </Text>
                ))}
            </View>

            {leaderboard.length >= 3 && (
                <View style={styles.podium}>
                    <View style={styles.podiumItem}>
                        <View style={[styles.podiumAvatar, styles.silver]}>
                            <Text style={styles.podiumInitial}>
                                {leaderboard[1]?.username?.charAt(0) || '2'}
                            </Text>
                        </View>
                        <Text style={styles.podiumName} numberOfLines={1}>
                            {leaderboard[1]?.username || 'N/A'}
                        </Text>
                        <Text style={styles.podiumPoints}>{leaderboard[1]?.points || 0}</Text>
                        <View style={[styles.podiumBase, styles.silverBase]}>
                            <Text style={styles.podiumRank}>2</Text>
                        </View>
                    </View>

                    <View style={[styles.podiumItem, styles.podiumFirst]}>
                        <Icon name="crown" size={24} color="#f39c12" style={styles.crown} />
                        <View style={[styles.podiumAvatar, styles.gold]}>
                            <Text style={styles.podiumInitial}>
                                {leaderboard[0]?.username?.charAt(0) || '1'}
                            </Text>
                        </View>
                        <Text style={styles.podiumName} numberOfLines={1}>
                            {leaderboard[0]?.username || 'N/A'}
                        </Text>
                        <Text style={styles.podiumPoints}>{leaderboard[0]?.points || 0}</Text>
                        <View style={[styles.podiumBase, styles.goldBase]}>
                            <Text style={styles.podiumRank}>1</Text>
                        </View>
                    </View>

                    <View style={styles.podiumItem}>
                        <View style={[styles.podiumAvatar, styles.bronze]}>
                            <Text style={styles.podiumInitial}>
                                {leaderboard[2]?.username?.charAt(0) || '3'}
                            </Text>
                        </View>
                        <Text style={styles.podiumName} numberOfLines={1}>
                            {leaderboard[2]?.username || 'N/A'}
                        </Text>
                        <Text style={styles.podiumPoints}>{leaderboard[2]?.points || 0}</Text>
                        <View style={[styles.podiumBase, styles.bronzeBase]}>
                            <Text style={styles.podiumRank}>3</Text>
                        </View>
                    </View>
                </View>
            )}
        </View>
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
                data={leaderboard.slice(3)}
                keyExtractor={(item, index) => item.id?.toString() || index.toString()}
                renderItem={({ item, index }) => (
                    <LeaderboardItem
                        entry={item}
                        rank={index + 4}
                        isCurrentUser={item.username === user?.username}
                    />
                )}
                ListHeaderComponent={renderHeader}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
                }
                contentContainerStyle={styles.listContent}
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
    headerContainer: {
        backgroundColor: '#667eea',
        paddingBottom: 20,
    },
    filterRow: {
        flexDirection: 'row',
        justifyContent: 'center',
        paddingVertical: 15,
    },
    filterTab: {
        paddingHorizontal: 20,
        paddingVertical: 8,
        marginHorizontal: 5,
        borderRadius: 20,
        backgroundColor: 'rgba(255,255,255,0.2)',
        color: '#fff',
        fontSize: 14,
    },
    filterTabActive: {
        backgroundColor: '#fff',
        color: '#667eea',
    },
    podium: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'flex-end',
        paddingHorizontal: 20,
        paddingTop: 20,
    },
    podiumItem: {
        alignItems: 'center',
        width: 100,
    },
    podiumFirst: {
        marginBottom: 20,
    },
    crown: {
        marginBottom: 5,
    },
    podiumAvatar: {
        width: 50,
        height: 50,
        borderRadius: 25,
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 8,
    },
    gold: {
        backgroundColor: '#f39c12',
    },
    silver: {
        backgroundColor: '#95a5a6',
    },
    bronze: {
        backgroundColor: '#cd6133',
    },
    podiumInitial: {
        color: '#fff',
        fontSize: 20,
        fontWeight: 'bold',
    },
    podiumName: {
        color: '#fff',
        fontSize: 12,
        fontWeight: '500',
        marginBottom: 4,
    },
    podiumPoints: {
        color: 'rgba(255,255,255,0.8)',
        fontSize: 11,
        marginBottom: 8,
    },
    podiumBase: {
        width: 40,
        height: 40,
        justifyContent: 'center',
        alignItems: 'center',
        borderTopLeftRadius: 5,
        borderTopRightRadius: 5,
    },
    goldBase: {
        backgroundColor: '#f39c12',
        height: 60,
    },
    silverBase: {
        backgroundColor: '#95a5a6',
        height: 45,
    },
    bronzeBase: {
        backgroundColor: '#cd6133',
        height: 35,
    },
    podiumRank: {
        color: '#fff',
        fontSize: 18,
        fontWeight: 'bold',
    },
    listContent: {
        paddingBottom: 20,
    },
});

export default LeaderboardScreen;
