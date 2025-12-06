import { defineConfig } from 'vite';

export default defineConfig({
  root: './', // Корневая директория проекта
  build: {
    outDir: 'coins/static/dist', // Выходная директория для собранных файлов
    emptyOutDir: true, // Очищать выходную директорию перед сборкой

    // Настройки Rollup для режима библиотеки
    rollupOptions: {
      input: {
        chart: './coins/static/js/chart.js', // Точка входа для вашей библиотеки
      },
      output: {
        // Убедитесь, что имена файлов не содержат хешей для простоты использования в Django static
        entryFileNames: `[name].js`, // Например, 'chart.js'
        chunkFileNames: `[name].js`,
        assetFileNames: `[name].[ext]`
      }
    },
    lib: {
      entry: './coins/static/js/chart.js', // Повторно указываем точку входа
      formats: ['es'], // ES Module формат
      fileName: () => 'chart.js' // Имя выходного файла
    }
  },
  server: {
    host: true, // Разрешает доступ к серверу извне контейнера
    port: 5173,
    watch: {
      usePolling: true // Включаем polling для Docker
    }
  }
});