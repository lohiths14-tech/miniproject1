import { StyleSheet, Text, View } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const LeaderboardItem = ({ entry, rank, isCurrentUser }) => {
    const getRankColor = (rank) => {
        if (rank === 1) return '#f39c12'; // Gold
        if (rank === 2) return '#95a5a6'; // Silver
        if (rank === 3) return '#cd6133'; // Bronze
        return '#667eea';
    };

    const getBadgeIcon = (badge) => {
        const icons = {
            'first_submission': 'rocket-launch',
            'streak_master': 'fire',
            'perfect_score': 'star',
            'code_ninja': 'ninja',
            'bug_hunter': 'bug',
            'speed_demon': 'lightning-bolt',
            'helper': 'hand-heart',
            'consistent': 'calendar-check',
        };
        return icons[badge?.type] || icons[badge] || 'medal';
    };

    return (
        <View style={[
            styles.container,
            isCurrentUser && styles.currentUserContainer
        ]}>
            <View style={[styles.rankContainer, { backgroundColor: getRankColor(rank) }]}>
                <Text style={styles.rankText}>{rank}</Text>
            </View>

            <View style={styles.avatarContainer}>
                <View style={styles.avatar}>
                    <Text style={styles.avatarText}>
                        {entry.username?.charAt(0)?.toUpperCase() || '?'}
                    </Text>
                </View>
            </View>

            <View style={styles.infoContainer}>
                <View style={styles.nameRow}>
                    <Text style={[
                        styles.username,
                        isCurrentUser && styles.currentUserText
                    ]} numberOfLines={1}>
                        {entry.username || 'Anonymous'}
                    </Text>
                    {isCurrentUser && (
                        <Text style={styles.youBadge}>You</Text>
                    )}
                </View>

                {entry.badges && entry.badges.length > 0 && (
                    <View style={styles.badgesRow}>
                        {entry.badges.slice(0, 3).map((badge, index) => (
                            <Icon
                                key={index}
                                name={getBadgeIcon(badge)}
                                size={14}
                                color="#f39c12"
                                style={styles.badgeIcon}
                            />
                        ))}
                        {entry.badges.length > 3 && (
                            <Text style={styles.moreBadges}>+{entry.badges.length - 3}</Text>
                        )}
                    </View>
                )}
            </View>

            <View style={styles.pointsContainer}>
                <Text style={styles.points}>{entry.points || 0}</Text>
                <Text style={styles.pointsLabel}>pts</Text>
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#fff',
        marginHorizontal: 15,
        marginVertical: 5,
        padding: 12,
        borderRadius: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
    },
    currentUserContainer: {
        backgroundColor: '#f0f4ff',
        borderWidth: 2,
        borderColor: '#667eea',
    },
    rankContainer: {
        width: 30,
        height: 30,
        borderRadius: 15,
        justifyContent: 'center',
        alignItems: 'center',
    },
    rankText: {
        color: '#fff',
        fontSize: 14,
        fontWeight: 'bold',
    },
    avatarContainer: {
        marginLeft: 12,
    },
    avatar: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#667eea',
        justifyContent: 'center',
        alignItems: 'center',
    },
    avatarText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
    infoContainer: {
        flex: 1,
        marginLeft: 12,
    },
    nameRow: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    username: {
        fontSize: 15,
        fontWeight: '600',
        color: '#333',
    },
    currentUserText: {
        color: '#667eea',
    },
    youBadge: {
        marginLeft: 8,
        paddingHorizontal: 6,
        paddingVertical: 2,
        backgroundColor: '#667eea',
        borderRadius: 8,
        color: '#fff',
        fontSize: 10,
        fontWeight: 'bold',
    },
    badgesRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 4,
    },
    badgeIcon: {
        marginRight: 4,
    },
    moreBadges: {
        fontSize: 11,
        color: '#999',
        marginLeft: 2,
    },
    pointsContainer: {
        alignItems: 'flex-end',
    },
    points: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#667eea',
    },
    pointsLabel: {
        fontSize: 11,
        color: '#999',
    },
});

export default LeaderboardItem;

