import AsyncStorage from '@react-native-async-storage/async-storage';
import { createContext, useContext, useEffect, useState } from 'react';
import api from '../services/api';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Load user from storage on mount
    useEffect(() => {
        loadUser();
    }, []);

    const loadUser = async () => {
        try {
            const userData = await AsyncStorage.getItem('@user');
            const token = await AsyncStorage.getItem('@token');

            if (userData && token) {
                setUser(JSON.parse(userData));
                api.setAuthToken(token);
            }
        } catch (error) {
            console.error('Failed to load user:', error);
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        try {
            const response = await api.post('/api/auth/login', {
                email,
                password
            });

            const { user: userData, token } = response.data;

            // Save to storage
            await AsyncStorage.setItem('@user', JSON.stringify(userData));
            await AsyncStorage.setItem('@token', token);

            // Set in state
            setUser(userData);
            api.setAuthToken(token);

            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Login failed'
            };
        }
    };

    const logout = async () => {
        try {
            await AsyncStorage.removeItem('@user');
            await AsyncStorage.removeItem('@token');
            setUser(null);
            api.setAuthToken(null);
        } catch (error) {
            console.error('Logout error:', error);
        }
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                login,
                logout
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
