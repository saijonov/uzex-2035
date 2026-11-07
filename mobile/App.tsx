import { StatusBar } from 'expo-status-bar'
import { useState } from 'react'
import { ActivityIndicator, Pressable, StyleSheet, Text, useColorScheme, View } from 'react-native'
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context'
import { WebView } from 'react-native-webview'

const APP_URL = process.env.EXPO_PUBLIC_APP_URL ?? 'http://localhost:8035'

export default function App() {
  const dark = useColorScheme() === 'dark'
  const [failed, setFailed] = useState(false)
  const [attempt, setAttempt] = useState(0)
  const background = dark ? '#0e0e10' : '#f2f2f6'

  return (
    <SafeAreaProvider>
      <SafeAreaView style={[styles.root, { backgroundColor: background }]} edges={['top']}>
        <StatusBar style={dark ? 'light' : 'dark'} />
        {failed ? (
          <View style={styles.center}>
            <Text style={[styles.text, { color: dark ? '#f2f2f4' : '#0d0d0f' }]}>Ilova ochilmadi. Internetni tekshiring.</Text>
            <Pressable
              style={styles.button}
              onPress={() => {
                setFailed(false)
                setAttempt(attempt + 1)
              }}
            >
              <Text style={styles.buttonText}>Qayta urinish</Text>
            </Pressable>
          </View>
        ) : (
          <WebView
            key={attempt}
            source={{ uri: APP_URL }}
            style={{ backgroundColor: background }}
            startInLoadingState
            renderLoading={() => <ActivityIndicator style={StyleSheet.absoluteFill} />}
            onError={() => setFailed(true)}
            bounces={false}
          />
        )}
      </SafeAreaView>
    </SafeAreaProvider>
  )
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 16, padding: 24 },
  text: { fontSize: 16, textAlign: 'center' },
  button: { backgroundColor: '#2a78d6', borderRadius: 14, paddingHorizontal: 24, paddingVertical: 14 },
  buttonText: { color: '#ffffff', fontSize: 16, fontWeight: '600' },
})
