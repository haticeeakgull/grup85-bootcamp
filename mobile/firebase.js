// firebase.js

import { initializeApp } from 'firebase/app';
// import { getAnalytics } from "firebase/analytics"; 
import Constants from 'expo-constants'; 
import { 
  initializeAuth, 
  getReactNativePersistence // <-- BURADA KALSIN!
} from 'firebase/auth'; // <-- BURADAN ALACAK
import ReactNativeAsyncStorage from '@react-native-async-storage/async-storage';

const firebaseConfig = Constants.expoConfig.extra.firebaseConfig;

const app = initializeApp(firebaseConfig);

const auth = initializeAuth(app, {
  persistence: getReactNativePersistence(ReactNativeAsyncStorage),
});

// const analytics = getAnalytics(app); 

export { auth };
export default app;