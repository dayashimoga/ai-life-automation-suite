import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import Constants from 'expo-constants';
import * as Notifications from 'expo-notifications';

const API = Constants.expoConfig?.extra?.habitApiUrl || 'http://localhost:8004';

// Push notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export default function HabitsScreen() {
  const [habits, setHabits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [logging, setLogging] = useState({});

  useEffect(() => {
    fetchHabits();
    // Register for push notifications
    registerForPushNotifications();
  }, []);

  async function registerForPushNotifications() {
    const { status } = await Notifications.requestPermissionsAsync();
    if (status !== 'granted') return;
    // Schedule "haven't logged today" reminder at 8pm
    await Notifications.scheduleNotificationAsync({
      content: {
        title: '🔥 Habit Reminder',
        body: "Don't break your streak! Log your habits for today.",
      },
      trigger: { hour: 20, minute: 0, repeats: true },
    });
  }

  async function fetchHabits() {
    try {
      const res = await fetch(`${API}/api/v1/habit/score`);
      const data = await res.json();
      setHabits(data);
    } catch (e) {
      console.error('Failed to fetch habits:', e);
    } finally {
      setLoading(false);
    }
  }

  async function logHabit(name) {
    setLogging(prev => ({ ...prev, [name]: true }));
    try {
      await fetch(`${API}/api/v1/habit/log`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ habit_name: name }),
      });
      fetchHabits();
    } finally {
      setLogging(prev => ({ ...prev, [name]: false }));
    }
  }

  if (loading) return <View style={s.center}><ActivityIndicator color="#6c63ff" /></View>;

  return (
    <View style={s.container}>
      <Text style={s.title}>🔥 My Habits</Text>
      <FlatList
        data={habits}
        keyExtractor={item => item.habit_name}
        renderItem={({ item }) => (
          <TouchableOpacity style={s.card} onPress={() => logHabit(item.habit_name)}>
            <View>
              <Text style={s.habitName}>{item.habit_name.replace(/_/g, ' ')}</Text>
              <Text style={s.streak}>{item.streak_days > 0 ? `🔥 ${item.streak_days} day streak` : 'Start your streak!'}</Text>
            </View>
            <Text style={s.score}>{Math.round(item.decayed_score)}</Text>
          </TouchableOpacity>
        )}
        contentContainerStyle={{ paddingBottom: 80 }}
      />
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a1a', padding: 16, paddingTop: 60 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0a0a1a' },
  title: { color: '#e2e8f0', fontSize: 26, fontWeight: '700', marginBottom: 20 },
  card: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 12, padding: 16, marginBottom: 10,
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)' },
  habitName: { color: '#e2e8f0', fontSize: 16, fontWeight: '600', textTransform: 'capitalize' },
  streak: { color: '#718096', fontSize: 13, marginTop: 4 },
  score: { color: '#6c63ff', fontSize: 24, fontWeight: '800' },
});
