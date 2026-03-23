import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import Constants from 'expo-constants';

const API = Constants.expoConfig?.extra?.doomscrollApiUrl || 'http://localhost:8002';

export default function FocusScreen() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/v1/usage/analytics`)
      .then(r => r.json()).then(setAnalytics)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <View style={s.center}><ActivityIndicator color="#6c63ff" /></View>;

  const risk = analytics?.average_risk ?? 0;
  const riskColor = risk > 0.6 ? '#fc8181' : risk > 0.3 ? '#f6ad55' : '#68d391';

  return (
    <View style={s.container}>
      <Text style={s.title}>🎯 Focus & Screen Time</Text>
      <View style={s.riskCard}>
        <Text style={s.riskLabel}>Doomscroll Risk</Text>
        <Text style={[s.riskValue, { color: riskColor }]}>{Math.round(risk * 100)}%</Text>
      </View>
      <View style={s.statsGrid}>
        <View style={s.statBox}>
          <Text style={s.statValue}>{analytics?.total_sessions ?? 0}</Text>
          <Text style={s.statLabel}>Sessions</Text>
        </View>
        <View style={s.statBox}>
          <Text style={s.statValue}>{analytics?.doomscroll_sessions ?? 0}</Text>
          <Text style={s.statLabel}>Risky Sessions</Text>
        </View>
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a1a', padding: 16, paddingTop: 60 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0a0a1a' },
  title: { color: '#e2e8f0', fontSize: 26, fontWeight: '700', marginBottom: 20 },
  riskCard: { backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 16, padding: 24,
    alignItems: 'center', marginBottom: 16 },
  riskLabel: { color: '#718096', fontSize: 14 },
  riskValue: { fontSize: 64, fontWeight: '800' },
  statsGrid: { flexDirection: 'row', gap: 12 },
  statBox: { flex: 1, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 12, padding: 16, alignItems: 'center' },
  statValue: { color: '#e2e8f0', fontSize: 32, fontWeight: '700' },
  statLabel: { color: '#718096', fontSize: 12, marginTop: 4 },
});
