import { StatusBar } from 'expo-status-bar'
import { useState } from 'react'
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native'
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context'
import { WebView } from 'react-native-webview'

const APP_URL = process.env.EXPO_PUBLIC_APP_URL ?? 'http://localhost:8035'

export default function App() {
  const [failed, setFailed] = useState(false)
  const [attempt, setAttempt] = useState(0)

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.root} edges={['top']}>
        <StatusBar style="dark" />
        {failed ? (
          <View style={styles.center}>
            <Text style={styles.text}>Приложение не открылось. Проверьте интернет.</Text>
            <Pressable
              style={styles.button}
              onPress={() => {
                setFailed(false)
                setAttempt(attempt + 1)
              }}
            >
              <Text style={styles.buttonText}>Повторить</Text>
            </Pressable>
          </View>
        ) : (
          <WebView
            key={attempt}
            source={{ uri: APP_URL }}
            style={styles.root}
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
  root: { flex: 1, backgroundColor: '#FFFFFF' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 16, padding: 24 },
  text: { fontSize: 16, textAlign: 'center', color: '#111111' },
  button: { backgroundColor: '#111111', borderRadius: 16, paddingHorizontal: 24, paddingVertical: 14 },
  buttonText: { color: '#FFDD2D', fontSize: 16, fontWeight: '700' },
})
