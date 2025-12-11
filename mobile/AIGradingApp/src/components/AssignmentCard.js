import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const AssignmentCard = ({ assignment, onPress }) => {
    const getStatusColor = (status) => {
        const colors = {
            pending: '#f39c12',
            submitted: '#3498db',
            graded: '#27ae60',
            overdue: '#e74c3c',
        };
        return colors[status] || '#95a5a6';
    };

    const getStatusIcon = (status) => {
        const icons = {
            pending: 'clock-outline',
            submitted: 'check-circle-outline',
            graded: 'check-decagram',
            overdue: 'alert-circle-outline',
        };
        return icons[status] || 'help-circle-outline';
    };

    const formatDueDate = (dateString) => {
        if (!dateString) return 'No due date';
        const date = new Date(dateString);
        const now = new Date();
        const diffDays = Math.ceil((date - now) / (1000 * 60 * 60 * 24));

        if (diffDays < 0) return 'Overdue';
        if (diffDays === 0) return 'Due today';
        if (diffDays === 1) return 'Due tomorrow';
        if (diffDays <= 7) return `Due in ${diffDays} days`;
        return date.toLocaleDateString();
    };

    const status = assignment.status || 'pending';
    const statusColor = getStatusColor(status);

    return (
        <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
            <View style={styles.content}>
                <View style={styles.header}>
                    <Text style={styles.title} numberOfLines={2}>
                        {assignment.title || 'Untitled Assignment'}
                    </Text>
                    <View style={[styles.statusBadge, { backgroundColor: statusColor }]}>
                        <Icon name={getStatusIcon(status)} size={12} color="#fff" />
                        <Text style={styles.statusText}>
                            {status.charAt(0).toUpperCase() + status.slice(1)}
                        </Text>
                    </View>
                </View>

                {assignment.description && (
                    <Text style={styles.description} numberOfLines={2}>
                        {assignment.description}
                    </Text>
                )}

                <View style={styles.footer}>
                    <View style={styles.dueDate}>
                        <Icon name="calendar-clock" size={14} color="#666" />
                        <Text style={styles.dueDateText}>
                            {formatDueDate(assignment.dueDate)}
                        </Text>
                    </View>

                    {assignment.points && (
                        <View style={styles.points}>
                            <Icon name="star" size={14} color="#f39c12" />
                            <Text style={styles.pointsText}>{assignment.points} pts</Text>
                        </View>
                    )}
                </View>

                {assignment.grade !== undefined && assignment.grade !== null && (
                    <View style={styles.gradeContainer}>
                        <Text style={styles.gradeLabel}>Grade:</Text>
                        <Text style={[
                            styles.gradeValue,
                            { color: assignment.grade >= 70 ? '#27ae60' : '#e74c3c' }
                        ]}>
                            {assignment.grade}%
                        </Text>
                    </View>
                )}
            </View>

            <Icon name="chevron-right" size={24} color="#ccc" style={styles.chevron} />
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: '#fff',
        borderRadius: 12,
        marginBottom: 12,
        flexDirection: 'row',
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    content: {
        flex: 1,
        padding: 15,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 8,
    },
    title: {
        fontSize: 16,
        fontWeight: '600',
        color: '#333',
        flex: 1,
        marginRight: 10,
    },
    statusBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 12,
    },
    statusText: {
        color: '#fff',
        fontSize: 11,
        fontWeight: '600',
        marginLeft: 4,
    },
    description: {
        fontSize: 13,
        color: '#666',
        marginBottom: 10,
        lineHeight: 18,
    },
    footer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    dueDate: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    dueDateText: {
        fontSize: 12,
        color: '#666',
        marginLeft: 5,
    },
    points: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    pointsText: {
        fontSize: 12,
        color: '#f39c12',
        marginLeft: 4,
        fontWeight: '500',
    },
    gradeContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 10,
        paddingTop: 10,
        borderTopWidth: 1,
        borderTopColor: '#f0f0f0',
    },
    gradeLabel: {
        fontSize: 13,
        color: '#666',
        marginRight: 5,
    },
    gradeValue: {
        fontSize: 15,
        fontWeight: 'bold',
    },
    chevron: {
        marginRight: 10,
    },
});

export default AssignmentCard;
