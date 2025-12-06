import { CandlestickSeries, createChart } from 'lightweight-charts';

document.addEventListener("DOMContentLoaded", function () {
  const chartData = JSON.parse(
    document.getElementById("chart-data").textContent
  );
  if (!chartData) {
    console.error("данные не перенеслись в js");
    return;
  }

  const chart = createChart(document.getElementById("chart"), {
    layout: {
      backgroundColor: "#ffffff",
      textColor: "#333",
    },
    grid: {
      vertLines: {
        color: "#e0e0e0",
      },
      horzLines: {
        color: "#e0e0e0",
      },
    },
    crosshair: {
      mode: 0, // CrosshairMode.Normal
    },
    leftpriceScale: {
      borderColor: "#e0e0e0",
      borderVisible: true,
      visible: true,
    },
    timeScale: {
      borderColor: "#e0e0e0",
      timeVisible: true,
      secondsVisible: false,
    },
  });

  // Добавляем свечной график
  const candlestickSeries = chart.addSeries(CandlestickSeries, {
    upColor: "#26a69a",
    downColor: "#ef5350",
    borderDownColor: "#ef5350",
    borderUpColor: "#26a69a",
    wickDownColor: "#ef5350",
    wickUpColor: "#26a69a",
  });

  candlestickSeries.setData(chartData);
  chart.timeScale().fitContent();
});