/**
 * static/js/main.js
 * Xử lý tương tác giao diện người dùng, gọi API AJAX, cập nhật biểu đồ Plotly và mô phỏng What-If.
 */

// Hàm đổi mã cổ phiếu nhanh trên Top Navbar
function changeGlobalSymbol(symbol) {
  const currentUrl = new URL(window.location.href);
  currentUrl.searchParams.set('symbol', symbol);
  window.location.href = currentUrl.toString();
}

// -------------------------------------------------------------
// VẼ BIỂU ĐỒ NẾN OHLCV & VOLUME (HISTORICAL DATA)
// -------------------------------------------------------------
function renderHistoricalCandlestickChart(containerId, symbol) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = '<div class="text-center py-5 text-muted"><div class="spinner-border text-primary me-2"></div>Đang tải dữ liệu biểu đồ...</div>';

  fetch(`/api/chart/historical/${symbol}`)
    .then(res => res.json())
    .then(data => {
      const traceCandle = {
        x: data.dates,
        open: data.open,
        high: data.high,
        low: data.low,
        close: data.close,
        type: 'candlestick',
        name: `Giá ${symbol}`,
        increasing: { line: { color: '#10b981' } },
        decreasing: { line: { color: '#ef4444' } },
        yaxis: 'y1'
      };

      const colorsVolume = data.close.map((c, i) => {
        if (i === 0) return 'rgba(16, 185, 129, 0.5)';
        return c >= data.close[i - 1] ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)';
      });

      const traceVolume = {
        x: data.dates,
        y: data.volume,
        type: 'bar',
        name: 'Khối Lượng Khớp Lệnh (Volume)',
        marker: { color: colorsVolume },
        yaxis: 'y2'
      };

      const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { t: 20, r: 40, l: 60, b: 40 },
        showlegend: false,
        font: { family: 'Plus Jakarta Sans', color: '#94a3b8' },
        xaxis: {
          gridcolor: 'rgba(255,255,255,0.05)',
          rangeslider: { visible: false }
        },
        yaxis: {
          title: 'Mức Giá (VNĐ)',
          gridcolor: 'rgba(255,255,255,0.05)',
          domain: [0.3, 1.0]
        },
        yaxis2: {
          title: 'Khối Lượng (CP)',
          gridcolor: 'rgba(255,255,255,0.02)',
          domain: [0.0, 0.25],
          showgrid: false
        }
      };

      const config = { responsive: true, displayModeBar: true, displaylogo: false };
      Plotly.newPlot(containerId, [traceCandle, traceVolume], layout, config);
    })
    .catch(err => {
      console.error(err);
      container.innerHTML = '<div class="alert alert-danger">Lỗi khi tải biểu đồ nến.</div>';
    });
}

// -------------------------------------------------------------
// VẼ BIỂU ĐỒ CHỈ SỐ KỸ THUẬT (INDICATORS)
// -------------------------------------------------------------
function renderTechnicalIndicatorsChart(containerId, symbol) {
  const container = document.getElementById(containerId);
  if (!container) return;

  fetch(`/api/chart/indicators/${symbol}`)
    .then(res => res.json())
    .then(data => {
      const traceClose = {
        x: data.dates,
        y: data.close,
        type: 'scatter',
        mode: 'lines',
        name: 'Giá Đóng Cửa (Close)',
        line: { color: '#ffffff', width: 2 },
        yaxis: 'y1'
      };

      const traceSMA20 = {
        x: data.dates,
        y: data.sma_20,
        type: 'scatter',
        mode: 'lines',
        name: 'Đường Trung Bình SMA 20 Ngày',
        line: { color: '#f59e0b', width: 1.5 },
        yaxis: 'y1'
      };

      const traceBBUpper = {
        x: data.dates,
        y: data.bb_upper,
        type: 'scatter',
        mode: 'lines',
        name: 'Dải Bollinger Trên (Upper)',
        line: { color: 'rgba(99, 102, 241, 0.5)', dash: 'dot' },
        yaxis: 'y1'
      };

      const traceBBLower = {
        x: data.dates,
        y: data.bb_lower,
        type: 'scatter',
        mode: 'lines',
        name: 'Dải Bollinger Dưới (Lower)',
        line: { color: 'rgba(99, 102, 241, 0.5)', dash: 'dot' },
        fill: 'tonexty',
        fillcolor: 'rgba(99, 102, 241, 0.05)',
        yaxis: 'y1'
      };

      const traceRSI = {
        x: data.dates,
        y: data.rsi_14,
        type: 'scatter',
        mode: 'lines',
        name: 'Chỉ Số Sức Mạnh Giá RSI (14)',
        line: { color: '#a855f7', width: 2 },
        yaxis: 'y2'
      };

      const traceMACD = {
        x: data.dates,
        y: data.macd,
        type: 'scatter',
        mode: 'lines',
        name: 'Đường Xu Hướng MACD (12, 26)',
        line: { color: '#06b6d4', width: 1.5 },
        yaxis: 'y3'
      };

      const traceMACDSignal = {
        x: data.dates,
        y: data.macd_signal,
        type: 'scatter',
        mode: 'lines',
        name: 'Đường Tín Hiệu Signal (9)',
        line: { color: '#ec4899', width: 1.5 },
        yaxis: 'y3'
      };

      const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { t: 20, r: 40, l: 60, b: 40 },
        font: { family: 'Plus Jakarta Sans', color: '#94a3b8' },
        legend: { orientation: 'h', y: 1.06 },
        grid: { rows: 3, columns: 1, pattern: 'independent' },
        xaxis: { gridcolor: 'rgba(255,255,255,0.05)' },
        yaxis: { title: 'Giá & Dải Bollinger', domain: [0.55, 1.0], gridcolor: 'rgba(255,255,255,0.05)' },
        yaxis2: { title: 'RSI (0 - 100)', domain: [0.28, 0.48], gridcolor: 'rgba(255,255,255,0.05)' },
        yaxis3: { title: 'MACD & Signal', domain: [0.0, 0.22], gridcolor: 'rgba(255,255,255,0.05)' }
      };

      const config = { responsive: true, displayModeBar: true, displaylogo: false };
      Plotly.newPlot(containerId, [traceClose, traceSMA20, traceBBUpper, traceBBLower, traceRSI, traceMACD, traceMACDSignal], layout, config);
    });
}

// -------------------------------------------------------------
// VẼ HEATMAP MA TRẬN NHẦM LẪN (CONFUSION MATRIX)
// -------------------------------------------------------------
function renderConfusionMatrix(containerId, cmData) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const zValues = cmData.matrix; // [[TN, FP], [FN, TP]]
  const xLabels = ['Dự đoán GIẢM (0)', 'Dự đoán TĂNG (1)'];
  const yLabels = ['Thực tế GIẢM (0)', 'Thực tế TĂNG (1)'];

  const data = [{
    z: zValues,
    x: xLabels,
    y: yLabels,
    type: 'heatmap',
    colorscale: [
      [0, '#1e293b'],
      [0.5, '#4338ca'],
      [1.0, '#10b981']
    ],
    showscale: false
  }];

  const annotations = [];
  const cellExplanations = [
    ['Đoán đúng GIẢM (TN)', 'Đoán nhầm TĂNG (FP)'],
    ['Đoán nhầm GIẢM (FN)', 'Đoán đúng TĂNG (TP)']
  ];

  for (let i = 0; i < 2; i++) {
    for (let j = 0; j < 2; j++) {
      annotations.push({
        x: xLabels[j],
        y: yLabels[i],
        text: `<b>${zValues[i][j]} phiên</b><br><span style="font-size:11px; color:#cbd5e1;">${cellExplanations[i][j]}</span>`,
        font: { color: '#ffffff', size: 14, family: 'Plus Jakarta Sans' },
        showarrow: false
      });
    }
  }

  const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: { t: 20, r: 20, l: 130, b: 60 },
    font: { family: 'Plus Jakarta Sans', color: '#94a3b8' },
    annotations: annotations,
    xaxis: { side: 'bottom' }
  };

  const config = { responsive: true, displayModeBar: false };
  Plotly.newPlot(containerId, data, layout, config);
}

// -------------------------------------------------------------
// VẼ ĐƯỜNG CONG ROC (ROC CURVE)
// -------------------------------------------------------------
function renderRocCurve(containerId, rocData, modelName) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const traceModel = {
    x: rocData.fpr,
    y: rocData.tpr,
    mode: 'lines',
    name: `${modelName} (Điểm AUC = ${rocData.auc})`,
    line: { color: '#6366f1', width: 3 }
  };

  const traceDiagonal = {
    x: [0, 1],
    y: [0, 1],
    mode: 'lines',
    name: 'Đường Đoán Ngẫu Nhiên (AUC = 0.50)',
    line: { color: '#64748b', dash: 'dash', width: 1.5 }
  };

  const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: { t: 20, r: 20, l: 55, b: 55 },
    font: { family: 'Plus Jakarta Sans', color: '#94a3b8' },
    legend: { orientation: 'h', y: -0.22 },
    xaxis: { title: 'Tỷ Lệ Báo Nhầm (FPR)', gridcolor: 'rgba(255,255,255,0.05)', range: [0, 1] },
    yaxis: { title: 'Tỷ Lệ Bắt Trúng TĂNG (TPR / Recall)', gridcolor: 'rgba(255,255,255,0.05)', range: [0, 1] }
  };

  const config = { responsive: true, displayModeBar: false };
  Plotly.newPlot(containerId, [traceModel, traceDiagonal], layout, config);
}

// -------------------------------------------------------------
// CÁC NÚT KỊCH BẢN MẪU (WHAT-IF PRESETS)
// -------------------------------------------------------------
function applySimulationPreset(presetType) {
  const rsiSlider = document.getElementById('simRsi');
  const macdSlider = document.getElementById('simMacd');
  const returnSlider = document.getElementById('simReturn');

  if (!rsiSlider || !macdSlider || !returnSlider) return;

  if (presetType === 'bullish') {
    rsiSlider.value = 65;
    macdSlider.value = 180;
    returnSlider.value = 3.5;
  } else if (presetType === 'bearish') {
    rsiSlider.value = 32;
    macdSlider.value = -220;
    returnSlider.value = -4.0;
  } else if (presetType === 'overbought') {
    rsiSlider.value = 82;
    macdSlider.value = 250;
    returnSlider.value = 6.0;
  } else if (presetType === 'oversold') {
    rsiSlider.value = 22;
    macdSlider.value = -300;
    returnSlider.value = -5.5;
  } else if (presetType === 'neutral') {
    rsiSlider.value = 50;
    macdSlider.value = 0;
    returnSlider.value = 0.0;
  }

  document.getElementById('valRsi').innerText = rsiSlider.value;
  document.getElementById('valMacd').innerText = macdSlider.value;
  document.getElementById('valReturn').innerText = (returnSlider.value > 0 ? '+' : '') + returnSlider.value + '%';

  if (typeof triggerLiveSimulation === 'function') {
    triggerLiveSimulation();
  }
}
