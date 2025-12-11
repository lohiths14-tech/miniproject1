import { useEffect, useState } from 'react';
import {
    ActivityIndicator,
    FlatList,
    RefreshControl,
    StyleSheet,
    Text,
    View,
} from 'react-native';
import AssignmentCard from '../components/AssignmentCard';
import api from '../services/api';

const AssignmentsScreen = ({ navigation }) => {
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [filter, setFilter] = useState('all'); // all, pending, submitted, graded

    useEffect(() => {
        fetchAssignments();
    }, []);

    const fetchAssignments = async () => {
        try {
            const response = await api.getAssignments();
            setAssignments(response.data.assignments || []);
        } catch (error) {
            console.error('Failed to fetch assignments:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const onRefresh = () => {
        setRefreshing(true);
        fetchAssignments();
    };

    const filteredAssignments = assignments.filter(assignment => {
        if (filter === 'all') return true;
        return assignment.status === filter;
    });

    const handleAssignmentPress = (assignment) => {
        navigation.navigate('AssignmentDetail', { assignment });
    };

    if (loading) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#667eea" />
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <View style={styles.filterContainer}>
                {['all', 'pending', 'submitted', 'graded'].map((f) => (
                    <Text
                        key={f}
                        style={[styles.filterTab, filter === f && styles.filterTabActive]}
                        onPress={() => setFilter(f)}
                    >
                        {f.charAt(0).toUpperCase() + f.slice(1)}
                    </Text>
                ))}
            </View>

            <FlatList
                data={filteredAssignments}
                keyExtractor={(item) => item.id?.toString() || item._id}
                renderItem={({ item }) => (
                    <AssignmentCard
                        assignment={item}
                        onPress={() => handleAssignmentPress(item)}
                    />
                )}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
                }
                contentContainerStyle={styles.listContent}
                ListEmptyComponent={
                    <View style={styles.emptyContainer}>
                        <Text style={styles.emptyText}>No assignments found</Text>
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
    filterContainer: {
        flexDirection: 'row',
        backgroundColor: '#fff',
        paddingVertical: 10,
        paddingHorizontal: 15,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
    },
    filterTab: {
        paddingHorizontal: 15,
        paddingVertical: 8,
        marginRight: 10,
        borderRadius: 20,
        backgroundColor: '#f0f0f0',
        color: '#666',
        fontSize: 14,
    },
    filterTabActive: {
        backgroundColor: '#667eea',
        color: '#fff',
    },
    listContent: {
        padding: 15,
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingTop: 50,
    },
    emptyText: {
        fontSize: 16,
        color: '#999',
    },
});

export default AssignmentsScreen;
