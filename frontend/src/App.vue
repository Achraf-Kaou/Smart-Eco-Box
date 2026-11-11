<template>
  <div class="min-h-screen bg-gray-100 text-gray-800">
    <!-- Header -->
    <header class="bg-green-700 text-white shadow-md">
      <div class="max-w-7xl mx-auto px-4 py-5 flex justify-between items-center">
        <h1 class="text-2xl font-bold">🌱 Smart Eco-Box</h1>
        <p class="text-sm opacity-90">Dashboard & Leaderboard</p>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <!-- Leaderboard -->
      <section class="lg:col-span-1 bg-white rounded-xl shadow-md p-6">
        <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
          🏆 Leaderboard
        </h2>

        <div v-if="leaderboard.length === 0" class="text-gray-500 text-sm">
          Aucune donnée pour le moment
        </div>

        <ul class="space-y-3">
          <li
            v-for="(user, index) in leaderboard"
            :key="user._id"
            class="flex items-center justify-between p-3 rounded-lg"
            :class="index === 0 ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50'"
          >
            <div class="flex items-center gap-3">
              <span class="font-bold text-lg w-6">{{ index + 1 }}</span>
              <div>
                <p class="font-medium">{{ user.user_name }}</p>
                <p class="text-xs text-gray-500">{{ user.totalDetections }} détections</p>
              </div>
            </div>
            <span class="font-bold text-green-700">{{ user.totalPoints }} pts</span>
          </li>
        </ul>
      </section>

      <!-- Recent Detections -->
      <section class="lg:col-span-2 bg-white rounded-xl shadow-md p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">📋 Dernières détections</h2>
          <button
            @click="fetchData"
            class="text-sm bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-md"
          >
            Actualiser
          </button>
        </div>

        <div v-if="detections.length === 0" class="text-gray-500 text-sm">
          Aucune détection enregistrée
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b text-left text-gray-600">
                <th class="pb-3">Utilisateur</th>
                <th class="pb-3">Déchet</th>
                <th class="pb-3">Points</th>
                <th class="pb-3">Confiance</th>
                <th class="pb-3">Date</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in detections"
                :key="item.event_id"
                class="border-b last:border-0 hover:bg-gray-50"
              >
                <td class="py-3 font-medium">{{ item.user_name }}</td>
                <td class="py-3">
                  <span
                    class="px-2 py-1 rounded-full text-xs font-medium"
                    :class="wasteColor(item.waste_type)"
                  >
                    {{ item.waste_type }}
                  </span>
                </td>
                <td class="py-3 font-semibold text-green-700">+{{ item.points }}</td>
                <td class="py-3">{{ (item.confidence * 100).toFixed(0) }}%</td>
                <td class="py-3 text-gray-500">
                  {{ formatDate(item.timestamp || item.createdAt) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API_URL = 'http://localhost:4020' // Change if needed

const detections = ref<any[]>([])
const leaderboard = ref<any[]>([])

const fetchData = async () => {
  try {
    const [detRes, leadRes] = await Promise.all([
      axios.get(`${API_URL}/detections/recent?limit=15`),
      axios.get(`${API_URL}/detections/leaderboard`),
    ])
    detections.value = detRes.data
    leaderboard.value = leadRes.data
  } catch (err) {
    console.error('Error fetching data:', err)
  }
}

const wasteColor = (type: string) => {
  const colors: Record<string, string> = {
    Plastique: 'bg-orange-100 text-orange-800',
    Métal: 'bg-yellow-100 text-yellow-800',
    'Papier / Carton': 'bg-pink-100 text-pink-800',
    'Non Recyclable': 'bg-red-100 text-red-800',
  }
  return colors[type] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  fetchData()
  // Auto-refresh every 8 seconds
  setInterval(fetchData, 8000)
})
</script>