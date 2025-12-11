import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// Screens
import AssignmentsScreen from './src/screens/AssignmentsScreen';
import CodeEditorScreen from './src/screens/CodeEditorScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import LeaderboardScreen from './src/screens/LeaderboardScreen';
import LoginScreen from './src/screens/LoginScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import SubmissionsScreen from './src/screens/SubmissionsScreen';

// Auth context
import { AuthProvider, useAuth } from './src/context/AuthContext';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Main tab navigator for authenticated users
function MainTabs() {
    return (
        <Tab.Navigator
            screenOptions={({ route }) => ({
                tabBarIcon: ({ focused, color, size }) => {
                    let iconName;

                    if (route.name === 'Dashboard') {
                        iconName = focused ? 'view-dashboard' : 'view-dashboard-outline';
                    } else if (route.name === 'Assignments') {
                        iconName = focused ? 'book-open-page-variant' : 'book-outline';
                    } else if (route.name === 'Leaderboard') {
                        iconName = focused ? 'trophy' : 'trophy-outline';
                    } else if (route.name === 'Profile') {
                        iconName = focused ? 'account' : 'account-outline';
                    }

                    return <Icon name={iconName} size={size} color={color} />;
                },
                tabBarActiveTintColor: '#667eea',
                tabBarInactiveTintColor: 'gray',
                headerStyle: {
                    backgroundColor: '#667eea',
                },
                headerTintColor: '#fff',
                headerTitleStyle: {
                    fontWeight: 'bold',
                },
            })}
        >
            <Tab.Screen name="Dashboard" component={DashboardScreen} />
            <Tab.Screen name="Assignments" component={AssignmentsScreen} />
            <Tab.Screen name="Leaderboard" component={LeaderboardScreen} />
            <Tab.Screen name="Profile" component={ProfileScreen} />
        </Tab.Navigator>
    );
}

// Main navigation stack
function AppNavigator() {
    const { user } = useAuth();

    return (
        <Stack.Navigator
            screenOptions={{
                headerStyle: {
                    backgroundColor: '#667eea',
                },
                headerTintColor: '#fff',
                headerTitleStyle: {
                    fontWeight: 'bold',
                },
            }}
        >
            {!user ? (
                // Auth screens
                <Stack.Screen
                    name="Login"
                    component={LoginScreen}
                    options={{ headerShown: false }}
                />
            ) : (
                // Main app screens
                <>
                    <Stack.Screen
                        name="Main"
                        component={MainTabs}
                        options={{ headerShown: false }}
                    />
                    <Stack.Screen
                        name="CodeEditor"
                        component={CodeEditorScreen}
                        options={{ title: 'Code Editor' }}
                    />
                    <Stack.Screen
                        name="Submissions"
                        component={SubmissionsScreen}
                        options={{ title: 'My Submissions' }}
                    />
                </>
            )}
        </Stack.Navigator>
    );
}

export default function App() {
    return (
        <AuthProvider>
            <NavigationContainer>
                <AppNavigator />
            </NavigationContainer>
        </AuthProvider>
    );
}
