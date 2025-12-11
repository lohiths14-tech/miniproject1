import { StyleSheet, Text, View } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const StatsCard = ({ icon, title, value, color, subtitle, trend }) => {
    const getTrendIcon = (trend) => {
        if (!trend) return null;
        if (trend > 0) return { icon: 'trending-up', color: '#27ae60' };
        if (trend < 0) return { icon: 'trending-down', color: '#e74c3c' };
        return { icon: 'trending-neutral', color: '#95a5a6' };
    };

    const trendConfig = getTrendIcon(trend);

    return (
        <View style={styles.card}>
            <View style={[styles.iconContainer, { backgroundColor: `${color}20` }]}>
                <Icon name={icon} size={24} color={color} />
            </View>

            <View style={styles.content}>
                <Text style={styles.title}>{title}</Text>
                <View style={styles.valueRow}>
                    <Text style={[styles.value, { color }]}>{value}</Text>
                    {trendConfig && (
                        <View style={styles.trendContainer}>
                            <Icon
                                name={trendConfig.icon}
                                size={14}
                                color={trendConfig.color}
                            />
                            <Text style={[styles.trendText, { color: trendConfig.color }]}>
                                {Math.abs(trend)}%
                            </Text>
                        </View>
                    )}
                </View>
                {subtitle && (
                    <Text style={styles.subtitle}>{subtitle}</Text>
                )}
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    card: {
        width: '48%',
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 15,
        marginBottom: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    iconContainer: {
        width: 44,
        height: 44,
        borderRadius: 22,
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 10,
    },
    content: {
        flex: 1,
    },
    title: {
        fontSize: 12,
        color: '#666',
        marginBottom: 4,
    },
    valueRow: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    value: {
        fontSize: 20,
        fontWeight: 'bold',
    },
    trendContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginLeft: 8,
    },
    trendText: {
        fontSize: 11,
        fontWeight: '500',
        marginLeft: 2,
    },
    subtitle: {
        fontSize: 11,
        color: '#999',
        marginTop: 4,
    },
});

export default StatsCard;
