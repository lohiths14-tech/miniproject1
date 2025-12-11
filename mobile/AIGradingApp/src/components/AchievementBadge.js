import { StyleSheet, Text, View } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const AchievementBadge = ({ achievement }) => {
    const getBadgeConfig = (type) => {
        const configs = {
            'first_submission': {
                icon: 'rocket-launch',
                color: '#3498db',
                label: 'First Steps',
            },
            'streak_master': {
                icon: 'fire',
                color: '#e74c3c',
                label: 'Streak Master',
            },
            'perfect_score': {
                icon: 'star',
                color: '#f39c12',
                label: 'Perfect Score',
            },
            'code_ninja': {
                icon: 'ninja',
                color: '#9b59b6',
                label: 'Code Ninja',
            },
            'bug_hunter': {
                icon: 'bug',
                color: '#27ae60',
                label: 'Bug Hunter',
            },
            'speed_demon': {
                icon: 'lightning-bolt',
                color: '#f1c40f',
                label: 'Speed Demon',
            },
            'helper': {
                icon: 'hand-heart',
                color: '#e91e63',
                label: 'Helper',
            },
            'consistent': {
                icon: 'calendar-check',
                color: '#00bcd4',
                label: 'Consistent',
            },
            'early_bird': {
                icon: 'weather-sunny',
                color: '#ff9800',
                label: 'Early Bird',
            },
            'night_owl': {
                icon: 'owl',
                color: '#673ab7',
                label: 'Night Owl',
            },
            'completionist': {
                icon: 'check-all',
                color: '#4caf50',
                label: 'Completionist',
            },
            'top_performer': {
                icon: 'trophy',
                color: '#ffc107',
                label: 'Top Performer',
            },
        };
        return configs[type] || {
            icon: 'medal',
            color: '#667eea',
            label: type || 'Achievement',
        };
    };

    const getLevelIndicator = (level) => {
        if (!level || level <= 1) return null;
        if (level === 2) return { color: '#c0c0c0', label: 'II' }; // Silver
        if (level === 3) return { color: '#ffd700', label: 'III' }; // Gold
        if (level >= 4) return { color: '#e5e4e2', label: 'IV' }; // Platinum
        return null;
    };

    const type = achievement?.type || achievement?.badge_type || achievement;
    const level = achievement?.level || 1;
    const config = getBadgeConfig(type);
    const levelIndicator = getLevelIndicator(level);

    return (
        <View style={styles.container}>
            <View style={[styles.badge, { backgroundColor: config.color }]}>
                <Icon name={config.icon} size={28} color="#fff" />
                {levelIndicator && (
                    <View style={[styles.levelBadge, { backgroundColor: levelIndicator.color }]}>
                        <Text style={styles.levelText}>{levelIndicator.label}</Text>
                    </View>
                )}
            </View>
            <Text style={styles.label} numberOfLines={1}>
                {achievement?.name || config.label}
            </Text>
            {achievement?.earnedAt && (
                <Text style={styles.date}>
                    {new Date(achievement.earnedAt).toLocaleDateString()}
                </Text>
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        alignItems: 'center',
        marginRight: 15,
        width: 80,
    },
    badge: {
        width: 60,
        height: 60,
        borderRadius: 30,
        justifyContent: 'center',
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.2,
        shadowRadius: 4,
        elevation: 4,
        position: 'relative',
    },
    levelBadge: {
        position: 'absolute',
        bottom: -2,
        right: -2,
        width: 20,
        height: 20,
        borderRadius: 10,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 2,
        borderColor: '#fff',
    },
    levelText: {
        fontSize: 8,
        fontWeight: 'bold',
        color: '#333',
    },
    label: {
        marginTop: 8,
        fontSize: 11,
        color: '#333',
        fontWeight: '500',
        textAlign: 'center',
    },
    date: {
        fontSize: 9,
        color: '#999',
        marginTop: 2,
    },
});

export default AchievementBadge;
