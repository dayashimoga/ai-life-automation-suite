import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Text, View, StyleSheet } from 'react-native';

// Import screens
import HabitsScreen from './screens/HabitsScreen';
import FocusScreen from './screens/FocusScreen';
import JournalScreen from './screens/JournalScreen';
import SecurityScreen from './screens/SecurityScreen';
import IntelligenceScreen from './screens/IntelligenceScreen';

const Tab = createBottomTabNavigator();

// Dark theme palette — matches the web Glassmorphism design system
const THEME = {
  background: '#0a0a1a',
  surface: 'rgba(255,255,255,0.05)',
  accent: '#6c63ff',
  text: '#e2e8f0',
  muted: '#718096',
};

const TAB_ICONS = {
  Habits: '🔥',
  Focus: '🎯',
  Journal: '📔',
  Security: '🔍',
  Intelligence: '🧠',
};

export default function App() {
  return (
    <NavigationContainer theme={{ colors: { background: THEME.background } }}>
      <StatusBar style="light" backgroundColor={THEME.background} />
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarStyle: {
            backgroundColor: THEME.surface,
            borderTopColor: 'rgba(255,255,255,0.1)',
            paddingBottom: 8,
            paddingTop: 4,
            height: 64,
          },
          tabBarActiveTintColor: THEME.accent,
          tabBarInactiveTintColor: THEME.muted,
          tabBarLabel: route.name,
          tabBarIcon: ({ size, color }) => (
            <Text style={{ fontSize: size * 0.8, opacity: color === THEME.accent ? 1 : 0.5 }}>
              {TAB_ICONS[route.name]}
            </Text>
          ),
        })}
      >
        <Tab.Screen name="Habits" component={HabitsScreen} />
        <Tab.Screen name="Focus" component={FocusScreen} />
        <Tab.Screen name="Intelligence" component={IntelligenceScreen} />
        <Tab.Screen name="Journal" component={JournalScreen} />
        <Tab.Screen name="Security" component={SecurityScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
