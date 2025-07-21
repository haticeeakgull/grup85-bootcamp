import React, { useState } from 'react';
import { AppRegistry, ActivityIndicator, View, StyleSheet } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginScreen from './screens/LoginScreen';
import RegisterScreen from './screens/RegisterScreen';
import HomeScreen from './screens/HomeScreen';

type Screen = 'login' | 'register';

function AuthenticatedApp() {
  const { user, loading } = useAuth();
  const [currentScreen, setCurrentScreen] = useState<Screen>('login');

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#1a3957" />
      </View>
    );
  }

  if (user) {
    return <HomeScreen />;
  }

  if (currentScreen === 'register') {
    return (
      <RegisterScreen 
        onNavigateToLogin={() => setCurrentScreen('login')} 
      />
    );
  }

  return (
    <LoginScreen 
      onNavigateToRegister={() => setCurrentScreen('register')} 
    />
  );
}

function App() {
  return (
    <AuthProvider>
      <AuthenticatedApp />
      <StatusBar style="auto" />
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
});

AppRegistry.registerComponent('main', () => App);

export default App;