import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  StatusBar,
  Alert,
  ActivityIndicator,
  // Image, // Eğer logonuz varsa Image bileşeni kalsın
} from 'react-native';
import * as ImagePicker from 'expo-image-picker'; 

// Sağlıklı Yaşam İpuçları Kartı için yardımcı bileşen
interface HealthTipCardProps {
  title: string;
  description: string;
}

const HealthTipCard: React.FC<HealthTipCardProps> = ({ title, description }) => (
  <View style={styles.card}>
    <View style={styles.tipIconContainer}>
      {/* iconName prop'u kaldırıldığı için placeholder kullanıyoruz */}
      <View style={styles.tipIconPlaceholder}></View>
      <Text style={styles.cardTitle}>{title}</Text>
    </View>
    <Text style={styles.cardText}>{description}</Text>
  </View>
);

export default function HomeScreen() {
  const [postureScore, setPostureScore] = useState(0); 
  const [analysisFeedback, setAnalysisFeedback] = useState("Henüz analiz yapılmadı.");
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false); 

  // Python API sunucunuzun güncel IP adresiyle değiştirildi
  const API_URL = 'http://192.168.42.207:5000/analyze-posture'; 

  const handleAnalyzePosture = async () => {
    // Kamera izni isteği
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('İzin Reddedildi', 'Kameraya erişim izni vermeniz gerekiyor.');
      return;
    }

    Alert.alert(
      "Analiz Seçimi",
      "Hangi egzersizi analiz etmek istersiniz?",
      [
        {
          text: "Squat Analizi",
          onPress: () => pickImageAndAnalyze('squat'),
        },
        {
          text: "Deadlift Analizi",
          onPress: () => pickImageAndAnalyze('deadlift'),
        },
        {
          text: "İptal",
          style: "cancel",
        },
      ]
    );
  };

  const pickImageAndAnalyze = async (exerciseType: 'squat' | 'deadlift') => {
    let result;
    try {
      result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: false, 
        quality: 0.7, 
        base64: true, 
      });

      if (result.canceled) {
        Alert.alert("İşlem İptal Edildi", "Fotoğraf çekme işlemi iptal edildi.");
        return;
      }

      if (!result.assets || result.assets.length === 0) {
        Alert.alert('Hata', 'Fotoğraf çekilemedi veya seçilemedi.');
        return;
      }

      const base64Image = result.assets[0].base64;

      if (!base64Image) {
        Alert.alert('Hata', 'Resim Base64 formatına çevrilemedi.');
        return;
      }

      setIsLoadingAnalysis(true);
      setAnalysisFeedback("Analiz ediliyor...");

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          image: base64Image, 
          exerciseType: exerciseType 
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setPostureScore(data.score);
        setAnalysisFeedback(data.feedback);
        Alert.alert("Analiz Başarılı", `Skorunuz: ${data.score}%\nGeribildirim: ${data.feedback}`);
      } else {
        setAnalysisFeedback(`Analiz hatası: ${data.error || 'Bilinmeyen Hata'}`);
        Alert.alert("Analiz Hatası", data.error || 'Sunucudan hata alındı');
      }
    } catch (error: any) {
      setAnalysisFeedback(`Ağ hatası: ${error.message}`);
      Alert.alert("Ağ Hatası", `Sunucuya bağlanılamadı. Python API'nizin çalıştığından ve doğru IP adresini kullandığınızdan emin olun. Hata: ${error.message}`);
      console.error("API çağrısı hatası:", error);
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  const healthTips = [
    {
      id: '1',
      title: 'Oturma Postürü',
      description: 'Bilgisayar başında otururken sırtınızı dik tutun, ayaklarınızı yere basın ve dizlerinizi 90 derece bükün.',
    },
    {
      id: '2',
      title: 'Ayakta Durma',
      description: 'Ayakta dururken ağırlığınızı iki ayağınıza eşit dağıtın ve omuzlarınızı geri çekin.',
    },
    {
      id: '3',
      title: 'Egzersiz Öncesi Isınma',
      description: 'Her egzersizden önce 5-10 dakika hafif tempolu ısınma hareketleri yapın.',
    },
  ];

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor={styles.headerBackground.backgroundColor} />
      <ScrollView contentContainerStyle={styles.scrollViewContent}>

        <View style={styles.headerBackground}>
          <Text style={styles.headerTitle}>TherapAI</Text>
          <Text style={styles.headerSubtitle}>Postür Analizi Asistanınız</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardHeaderTitle}>Hoş Geldiniz!</Text>
          <Text style={styles.cardText}>
            Doğru postürü keşfedin, sağlıklı ve güçlü bir yaşama adım atın!
          </Text>
        </View>

        <TouchableOpacity 
          style={styles.primaryButton} 
          onPress={handleAnalyzePosture} 
          disabled={isLoadingAnalysis} 
        >
          <Text style={styles.primaryButtonText}>
            {isLoadingAnalysis ? <ActivityIndicator color="#fff" /> : 'Analiz Başla'}
          </Text>
        </TouchableOpacity>

        <Text style={styles.sectionTitle}>Son Durumunuz</Text>
        <View style={styles.card}>
          <Text style={styles.cardHeaderTitle}>Son Analiz Özeti:</Text>
          <Text style={styles.statusText}>
            {analysisFeedback} 
          </Text>
        </View>

        <Text style={styles.sectionTitle}>İlerleme Takibi</Text>
        <View style={styles.card}>
          <Text style={styles.cardHeaderTitle}>Haftalık Ortalama Postür Skoru:</Text>
          <View style={styles.progressBarBackground}>
            <View style={[styles.progressBarFill, { width: `${postureScore}%` }]}></View>
          </View>
          <Text style={styles.progressBarText}>{postureScore.toFixed(1)}%</Text>
        </View>

        <Text style={styles.sectionTitle}>Sağlıklı Yaşam İpuçları</Text>
        {healthTips.map((tip) => (
          <HealthTipCard
            key={tip.id}
            title={tip.title}
            description={tip.description}
          />
        ))}

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
  scrollViewContent: {
    paddingHorizontal: 20,
    paddingVertical: 20,
    paddingTop: 0,
  },
  headerBackground: {
    backgroundColor: '#2E4A62',
    paddingVertical: 40,
    alignItems: 'center',
    marginBottom: 25,
    borderBottomLeftRadius: 25,
    borderBottomRightRadius: 25,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 8,
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  headerSubtitle: {
    fontSize: 17,
    color: '#E0E0E0',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 24,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 15,
    padding: 22,
    marginBottom: 18,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 7,
    elevation: 5,
  },
  cardHeaderTitle: {
    fontSize: 19,
    fontWeight: '700',
    color: '#2E4A62',
    marginBottom: 10,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2E4A62',
    marginBottom: 5,
  },
  cardText: {
    fontSize: 15,
    color: '#6C757D',
    lineHeight: 23,
  },
  primaryButton: {
    backgroundColor: '#2E4A62',
    paddingVertical: 18,
    borderRadius: 15,
    alignItems: 'center',
    marginBottom: 25,
    shadowColor: '#2E4A62',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.25,
    shadowRadius: 10,
    elevation: 8,
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 22,
    fontWeight: 'bold',
    letterSpacing: 0.7,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#2E4A62',
    marginBottom: 18,
    marginTop: 10,
  },
  statusText: {
    fontSize: 16,
    color: '#2E4A62',
    fontWeight: '500',
  },
  progressBarBackground: {
    height: 14,
    backgroundColor: '#E0E0E0',
    borderRadius: 7,
    overflow: 'hidden',
    marginBottom: 12,
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#28A745',
    borderRadius: 7,
  },
  progressBarText: {
    fontSize: 17,
    color: '#6C757D',
    textAlign: 'right',
    fontWeight: '600',
  },
  tipIconContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  tipIconPlaceholder: {
    width: 30,
    height: 30,
    backgroundColor: '#A0A0A0',
    borderRadius: 8,
    marginRight: 15,
  },
});