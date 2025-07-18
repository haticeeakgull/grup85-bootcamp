import React from 'react';
import { AppRegistry } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import LoginScreen from './screens/LoginScreen';

function App() {
  return (
    <>
      <LoginScreen />
      <StatusBar style="auto" />
    </>
  );
}

AppRegistry.registerComponent('main', () => App);

export default App;