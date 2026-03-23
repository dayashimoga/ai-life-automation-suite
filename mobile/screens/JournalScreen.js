import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from 'react-native';
import Constants from 'expo-constants';

const API = Constants.expoConfig?.extra?.journalApiUrl || 'http://localhost:8001';

export default function JournalScreen() {
  const [wellness, setWellness] = useState(null);
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/v1/journal/wellness`).then(r => r.json()),
      fetch(`${API}/api/v1/journal/timeline`).then(r => r.json()),
    ]).then(([w, t]) => {
      setWellness(w);
      setEntries(t.entries || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <View style={s.center}><ActivityIndicator color="#6c63ff" /></View>;

  const riskColor = (wellness?.burnout_risk ?? 0) > 0.5 ? '#fc8181' : '#68d391';

  return (
    <View style={s.container}>
      <Text style={s.title}>📔 Memory Journal</Text>
      {wellness && (
        <View style={s.wellnessCard}>
          <Text style={s.wellnessLabel}>Burnout Risk</Text>
          <Text style={[s.wellnessValue, { color: riskColor }]}>
            {Math.round(wellness.burnout_risk * 100)}%
          </Text>
          <Text style={s.recommendation}>{wellness.recommendation}</Text>
        </View>
      )}
      <FlatList
        data={entries.slice(0, 10)}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <View style={s.entry}>
            <Text style={s.caption}>{item.caption || item.filename}</Text>
            <Text style={s.date}>{new Date(item.created_at).toLocaleDateString()}</Text>
          </View>
        )}
        contentContainerStyle={{ paddingBottom: 80 }}
      />
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a1a', padding: 16, paddingTop: 60 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0a0a1a' },
  title: { color: '#e2e8f0', fontSize: 26, fontWeight: '700', marginBottom: 16 },
  wellnessCard: { backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 16, padding: 20, marginBottom: 16 },
  wellnessLabel: { color: '#718096', fontSize: 13 },
  wellnessValue: { fontSize: 48, fontWeight: '800' },
  recommendation: { color: '#a0aec0', fontSize: 13, marginTop: 8, lineHeight: 20 },
  entry: { borderRadius: 10, backgroundColor: 'rgba(255,255,255,0.04)', padding: 12, marginBottom: 8 },
  caption: { color: '#e2e8f0', fontSize: 14 },
  date: { color: '#718096', fontSize: 11, marginTop: 4 },
});
