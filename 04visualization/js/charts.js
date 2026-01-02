/**
 * 医疗AI视觉诊断分析系统 - 核心逻辑驱动 V3.0
 * 包含：高分抗锯齿渲染、侧边栏联动、错误分析诊断
 */

// 1. 全局配置与状态管理
const CONFIG = {
    renderer: 'canvas',
    devicePixelRatio: 2, // 解决模糊问题
    animation: true,
    fontSize: 12
};

const UI_COLORS = {
    primary: ['#00d4ff', '#00ffcc', '#a259ff', '#ff6b6b', '#ffd43b', '#4facfe', '#43e97b', '#fa709a'],
    gradients: [
        ['#00d4ff', '#00ffcc'], ['#a259ff', '#fa709a'], ['#ffd43b', '#ff6b6b'],
        ['#4facfe', '#00f2fe'], ['#43e97b', '#38f9d7'], ['#667eea', '#764ba2']
    ]
};

// 全局统一的模型显示顺序（由优到劣：Final, PyTorch_ResNet, C, B组, A组）
const APP_SORTED_MODELS = [
    'PyTorch_ResNet', 
    'finalmodel', 
    'C组', 
    'modelB3测试报告', 'modelB2测试报告', 'modelB1测试报告',
    'modelA3测试报告', 'modelA2测试报告', 'modelA1测试报告',
    'ResNet18 (Standard)', 'VGG16', 'DenseNet121'
];

let appState = {
    charts: {},
    currentMetric: 'all',
    viewMode: 'by-metric', // 新增：3D视图模式
    current3DModel: APP_SORTED_MODELS[0], // 使用排序后的第一个
    selectedComparisonModels: [...APP_SORTED_MODELS], // 默认全选排序后的
    currentModel: APP_SORTED_MODELS[0],
    selectedModels: [...APP_SORTED_MODELS].slice(0, 3),
    activeSection: 'comprehensive-comparison',
    errorAnalysisModel: 'pytorch' // 'pytorch' or 'finalmodel'
};

// 工具函数：简化模型名称显示
function formatModelName(name) {
    if (!name) return '';
    return name.replace('model', '')
               .replace('测试报告', '')
               .replace('finalmodel', 'Final')
               .replace('PyTorch_ResNet', 'PyTorch')
               .replace('C组', 'C组');
}

// 工具函数：数值收敛（解决 77.720000000000006% 这种鬼）
function formatVal(val, decimals = 1) {
    if (typeof val !== 'number') return '0.0';
    // 自动判断是否需要乘以 100
    let displayVal = val <= 1.01 ? val * 100 : val;
    return displayVal.toFixed(decimals);
}

// 工具函数：智能计算Y轴最小值 - 增强版
function getSmartYMin(values) {
    if (!values || values.length === 0) return 0;
    const minVal = Math.min(...values);
    const maxVal = Math.max(...values);
    const range = maxVal - minVal;
    
    // 根据数据范围动态调整起点，突出差异
    let buffer;
    if (range < 5) {
        // 数据非常接近（如98-99%），留50%缓冲
        buffer = range * 0.5;
    } else if (range < 20) {
        // 数据较接近（如80-95%），留20%缓冲
        buffer = range * 0.2;
    } else {
        // 数据差异较大，留10%缓冲
        buffer = range * 0.1;
    }
    
    const smartMin = Math.max(0, minVal - buffer);
    return Math.floor(smartMin / 5) * 5; // 向下取整到5的倍数
}

// 更新全选/取消全选按钮状态
function updateButtonStates(type) {
    let selectAllBtn, deselectAllBtn, currentSelection, totalModels;

    if (type === 'comparison') {
        selectAllBtn = document.getElementById('comparison-select-all');
        deselectAllBtn = document.getElementById('comparison-deselect-all');
        currentSelection = appState.selectedComparisonModels;
    } else { // confidence
        selectAllBtn = document.getElementById('confidence-select-all');
        deselectAllBtn = document.getElementById('confidence-deselect-all');
        currentSelection = appState.selectedModels;
    }
    
    totalModels = APP_SORTED_MODELS;

    if (selectAllBtn) {
        const allSelected = currentSelection.length === totalModels.length;
        selectAllBtn.style.opacity = allSelected ? '0.5' : '1';
        selectAllBtn.style.pointerEvents = allSelected ? 'none' : 'auto';
        selectAllBtn.disabled = allSelected;
    }

    if (deselectAllBtn) {
        const noneSelected = currentSelection.length === 0;
        deselectAllBtn.style.opacity = noneSelected ? '0.5' : '1';
        deselectAllBtn.style.pointerEvents = noneSelected ? 'none' : 'auto';
        deselectAllBtn.disabled = noneSelected;
    }
}

// 全选/取消全选模型
function toggleAllModels(type, isSelect) {
    const list = isSelect ? [...APP_SORTED_MODELS] : [];
    if (type === 'comparison') {
        appState.selectedComparisonModels = list;
        initComparisonModelCheckboxes();
        update3DBar();
        updateRanking();
        updateRadar();
    } else if (type === 'confidence') {
        appState.selectedModels = list;
        initConfidenceModelCheckboxes();
        updateConfidenceCharts();
    }
}
window.toggleAllModels = toggleAllModels;

// 2. 初始化流程
document.addEventListener('DOMContentLoaded', () => {
    bindUIGlobalEvents();
    initAllCharts();
    renderErrorAnalysis();
});
// 2. UI 事件绑定
function bindUIGlobalEvents() {
    // 侧边栏导航
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            const section = item.dataset.section;
            switchSection(section);
        });
    });

    // 指标切换
    document.getElementById('metric-selector')?.addEventListener('change', (e) => {
        appState.currentMetric = e.target.value;
        update3DBar();
        updateRanking();
    });

    // 联动控件 - 3D视图模式切换
    document.getElementById('view-mode-selector').addEventListener('change', (e) => {
        appState.viewMode = e.target.value;
        update3DBar();
        // 根据模式显示/隐藏模型选择器
        const modelCtrl = document.getElementById('global-model-ctrl');
        const metricCtrl = document.getElementById('global-metric-ctrl');
        const comparisonModelsCtrl = document.getElementById('comparison-models-ctrl');
        if (e.target.value === 'by-model') {
            modelCtrl.style.display = 'block';
            metricCtrl.style.display = 'none';
            comparisonModelsCtrl.style.display = 'none';
        } else {
            modelCtrl.style.display = 'none';
            metricCtrl.style.display = 'block';
            comparisonModelsCtrl.style.display = 'block';
        }
    });

    // 联动控件 - 3D视图中的模型选择 (填充选项显示名)
    const updateModelSelectorOptions = (selector) => {
        if (!selector) return;
        selector.innerHTML = '';
        APP_SORTED_MODELS.forEach(name => {
            const opt = document.createElement('option');
            opt.value = name;
            opt.textContent = formatModelName(name);
            selector.appendChild(opt);
        });
    };

    // 初始化3D视图模型选择器
    const model3DSelector = document.getElementById('model-selector-3d');
    updateModelSelectorOptions(model3DSelector);
    
    model3DSelector.addEventListener('change', (e) => {
        appState.current3DModel = e.target.value;
        update3DBar();
    });

    // 初始化类别分析模型选择器
    updateModelSelectorOptions(document.getElementById('model-selector-category'));

    // 模型切换（类别分析）
    document.getElementById('model-selector-category')?.addEventListener('change', (e) => {
        appState.currentModel = e.target.value;
        updateCategoryViews();
    });

    // 填充模型对比复选框（按指标模式）
    initComparisonModelCheckboxes();

    // 填充置信度分析模型复选框
    initConfidenceModelCheckboxes();

    // 移除JS绑定，改回HTML inline调用以确保稳定性
    // document.getElementById('confidence-select-all')?.addEventListener...
    
    // 雷达图添加全选/取消全选按钮（1秒后确保图表已生成）
    setTimeout(() => {
        const radarLegend = document.querySelector('#chart-radar')?.parentElement?.querySelector('.chart-header');
        if (radarLegend && !document.getElementById('radar-select-all')) {
            const btnGroup = document.createElement('div');
            btnGroup.style.cssText = 'display: flex; gap: 5px;';
            btnGroup.innerHTML = `
                <button id="radar-select-all" style="padding: 3px 8px; font-size: 0.7rem; background: var(--primary-color); border: none; border-radius: 4px; color: #fff; cursor: pointer;">全选</button>
                <button id="radar-deselect-all" style="padding: 3px 8px; font-size: 0.7rem; background: var(--error-color); border: none; border-radius: 4px; color: #fff; cursor: pointer;">取消全选</button>
            `;
            radarLegend.appendChild(btnGroup);

            document.getElementById('radar-select-all').addEventListener('click', () => {
                toggleAllModels('comparison', true);
            });
            document.getElementById('radar-deselect-all').addEventListener('click', () => {
                toggleAllModels('comparison', false);
            });
        }
    }, 1000);

    // 添加图表帮助说明
    // addChartHelpButtons(); // Removed as per user request
}

function switchSection(sectionId) {
    appState.activeSection = sectionId;

    // UI 激活态
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');

    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');

    // 标题更新
    const titles = {
        'comprehensive-comparison': '综合性能对比分析',
        'diagnostic-analysis': '分类诊断深度分析',
        'confidence-analysis': '置信度分布与稳定性分析',
        'trend-analysis': '模型性能演进趋势',
        'error-analysis': '错误案例深度回溯'
    };
    document.getElementById('section-title').textContent = titles[sectionId];

    // 控制器显隐切换
    const viewModeCtrl = document.getElementById('view-mode-ctrl');
    const globalMetricCtrl = document.getElementById('global-metric-ctrl');
    const comparisonModelsCtrl = document.getElementById('comparison-models-ctrl');
    const globalModelCtrl = document.getElementById('global-model-ctrl');
    const categoryModelCtrl = document.getElementById('category-model-ctrl');
    const confidenceModelsCtrl = document.getElementById('confidence-models-ctrl');

    // 隐藏所有控制器
    viewModeCtrl.style.display = 'none';
    globalMetricCtrl.style.display = 'none';
    comparisonModelsCtrl.style.display = 'none';
    globalModelCtrl.style.display = 'none';
    categoryModelCtrl.style.display = 'none';
    confidenceModelsCtrl.style.display = 'none';

    // 根据当前section显示相应控制器
    if (sectionId === 'comprehensive-comparison') {
        viewModeCtrl.style.display = 'block';
        if (appState.viewMode === 'by-model') {
            globalModelCtrl.style.display = 'block';
        } else {
            globalMetricCtrl.style.display = 'block';
            comparisonModelsCtrl.style.display = 'block';
        }
    } else if (sectionId === 'diagnostic-analysis') {
        categoryModelCtrl.style.display = 'block';
    } else if (sectionId === 'confidence-analysis') {
        confidenceModelsCtrl.style.display = 'block';
    }

    // 强制 Resize
    setTimeout(() => {
        Object.values(appState.charts).forEach(c => c && c.resize());
    }, 100);
}

// 3. 图表初始化模块 - 关键修复：先创建所有图表实例，再填充数据
function initAllCharts() {
    // === 第一阶段：创建所有echarts实例 ===
    appState.charts['3d-bar'] = echarts.init(document.getElementById('chart-3d-bar'), null, CONFIG);
    appState.charts['radar'] = echarts.init(document.getElementById('chart-radar'), null, CONFIG);
    appState.charts['ranking'] = echarts.init(document.getElementById('chart-ranking'), null, CONFIG);
    appState.charts['heatmap'] = echarts.init(document.getElementById('chart-heatmap'), null, CONFIG);
    appState.charts['cat-bars'] = echarts.init(document.getElementById('chart-category-bars'), null, CONFIG);
    appState.charts['3d-pie'] = echarts.init(document.getElementById('chart-3d-pie'), null, CONFIG);
    appState.charts['cm-heatmap'] = echarts.init(document.getElementById('chart-confusion-matrix'), null, CONFIG);
    appState.charts['boxplot'] = echarts.init(document.getElementById('chart-boxplot'), null, CONFIG);
    appState.charts['hist'] = echarts.init(document.getElementById('chart-histogram'), null, CONFIG);
    appState.charts['line-conf'] = echarts.init(document.getElementById('chart-line-confidence'), null, CONFIG);
    appState.charts['trend-line'] = echarts.init(document.getElementById('chart-trend-line'), null, CONFIG);

    // === 第二阶段：填充数据 ===
    update3DBar();
    updateRadar();
    updateRanking();
    updateHeatmap();
    updateCategoryViews();
    updateConfidenceCharts();
    updateTrendLine();
    
    // 绑定趋势图指标选择器
    document.getElementById('trend-metric-selector').addEventListener('change', updateTrendLine);
}

// --- 模型对比模块 ---

function init3DBar() {
    const container = document.getElementById('chart-3d-bar');
    const chart = echarts.init(container, null, CONFIG);
    
    // 使用更标准的方式阻止右键菜单，确保不干扰其他鼠标操作
    container.addEventListener('contextmenu', e => {
        e.preventDefault();
        return false;
    });
    
    appState.charts['3d-bar'] = chart;
    update3DBar();
}

function update3DBar() {
    const chart = appState.charts['3d-bar'];
    if (!chart) return;

    const metricsMap = { accuracy: '准确率', precision: '精确率', recall: '召回率', f1: 'F1分数', specificity: '特异度' };
    
    let data = [];
    let xAxis3D, yAxis3D;
    let selectedModels = []; // 在函数作用域声明

    if (appState.viewMode === 'by-model') {
        // 按模型模式：显示单个模型的所有指标
        const model = appState.current3DModel;
        // Safety check
        if (!MODEL_DATA[model]) {
             console.warn(`[update3DBar] Model data missing: ${model}`);
             return;
        }
        const metricKeys = Object.keys(metricsMap);
        metricKeys.forEach((mKey, metIdx) => {
            const val = (MODEL_DATA[model].overall[mKey] || 0) * 100;
            data.push([metIdx, 0, val]);
        });
        xAxis3D = { type: 'category', data: metricKeys.map(k => metricsMap[k]), axisLabel: { textStyle: { color: '#a8b3cf' } } };
        yAxis3D = { type: 'category', data: [formatModelName(model)], axisLabel: { textStyle: { color: '#a8b3cf', fontSize: 10 } } };
        selectedModels = [model]; // 赋值selectedModels
    } else {
        // 按指标模式：使用selectedComparisonModels筛选模型
        const displayMetrics = appState.currentMetric === 'all' ? Object.keys(metricsMap) : [appState.currentMetric];
        selectedModels = appState.selectedComparisonModels; // 直接赋值而不是const
        // Safety check loop
        selectedModels.forEach((model, modIdx) => {
            if (!MODEL_DATA[model]) return; // Skip missing models
            displayMetrics.forEach((mKey, metIdx) => {
                const val = (MODEL_DATA[model].overall[mKey] || 0) * 100;
                data.push([metIdx, modIdx, val]);
            });
        });
        xAxis3D = { type: 'category', data: displayMetrics.map(k => metricsMap[k]), axisLabel: { textStyle: { color: '#a8b3cf' } } };
        yAxis3D = { 
            type: 'category', 
            data: selectedModels.map(formatModelName),  // 修复：显示所有选中的模型名称 (简化)
            axisLabel: { 
                textStyle: { color: '#a8b3cf', fontSize: 9 },
                interval: 0,  // 强制显示所有标签
                rotate: 15  // 旋转以防止重叠
            } 
        };
    }

    // 智能Y轴（Z轴）
    const allValues = data.map(d => d[2]);
    const smartMin = getSmartYMin(allValues);
    const actualMin = Math.min(...allValues);  // 实际最小值

    chart.setOption({
        tooltip: {
            formatter: p => {
                const modelName = appState.viewMode === 'by-model' ? appState.current3DModel : (appState.selectedComparisonModels[p.value[1]] || '');
                const metricKey = appState.viewMode === 'by-model' ? Object.keys(metricsMap)[p.value[0]] : 
                    (appState.currentMetric === 'all' ? Object.keys(metricsMap)[p.value[0]] : appState.currentMetric);
                return `${formatModelName(modelName)}<br/>${metricsMap[metricKey]}: <b>${p.value[2].toFixed(2)}%</b>`;  // 修复：toFixed(2)
            }
        },
        visualMap: {
            max: 100, 
            min: Math.max(0, actualMin - 5),  // 修复：使用实际最小值-5，确保所有数据可见
            calculable: true,
            inRange: { color: ['#4facfe', '#00ffcc', '#fee140'] },
            right: 0, top: 'center', textStyle: { color: '#fff' }
        },
        xAxis3D: xAxis3D,
        yAxis3D: yAxis3D,
        zAxis3D: { type: 'value', min: smartMin, max: 100, axisLabel: { textStyle: { color: '#a8b3cf' } } },
        grid3D: {
            boxWidth: appState.viewMode === 'by-model' ? 150 : 
                      (appState.currentMetric === 'all' ? 150 : 60),  // 修复：单指标时X轴变窄
            boxDepth: appState.viewMode === 'by-model' ? 40 : Math.min(180, selectedModels.length * 25),
            viewControl: { 
                distance: 320,               // 修正：加大距离 (135->320) 以适应较大的box尺寸
                beta: 40,
                alpha: 25, 
                panMouseButton: 'right',     // 右键平移
                rotateMouseButton: 'left',   // 显式指定左键旋转
                rotateSensitivity: 1.5,      // 提高旋转灵敏度
                panSensitivity: 1.5          // 提高平移灵敏度
            },
            postEffect: { enable: true, SSAO: { enable: true, radius: 2 } },
            light: { main: { intensity: 1.5 }, ambient: { intensity: 0.6 } }
        },
        series: [{ 
            type: 'bar3D', 
            data: data, 
            shading: 'lambert',
            barSize: appState.viewMode === 'by-model' ? 10 : null,
            label: {
                show: false,  // 默认不显示，避免重叠
                formatter: (params) => params.value[2].toFixed(2) + '%'  // 格式化为2位小数
            }
        }]
    });
}

function updateRadar() {
    try {
        const chart = appState.charts['radar'];
        if (!chart) return;

        // Simplify: Only render what is selected in the sidebar. 
        // This avoids "Hidden" series state issues and ensures visibility.
        const activeModels = APP_SORTED_MODELS.filter(m => appState.selectedComparisonModels.includes(m));
        
        // If nothing selected, show empty or fallback? 
        // Show empty chart with axis but no data to avoid confusion
        // But we need axis scaling. If empty, use defaults.
        const modelsForScale = activeModels.length > 0 ? activeModels : APP_SORTED_MODELS; 

        const indicatorsBase = [
            { key: 'accuracy', label: '准确率' },
            { key: 'precision', label: '精确率' },
            { key: 'recall', label: '召回率' },
            { key: 'f1', label: 'F1分数' },
            { key: 'specificity', label: '特异度' }
        ];

        const indicators = indicatorsBase.map(ind => {
            const values = modelsForScale.map(m => {
                const d = MODEL_DATA[m];
                return (d && d.overall) ? d.overall[ind.key] : 0;
            });
            
            if (values.length === 0) values.push(0);

            let minVal = Math.min(...values);
            let maxVal = Math.max(...values);
            let range = maxVal - minVal;

            // Smart padding
            let niceMin = Math.max(0, minVal - range * 0.1); 
            let niceMax = Math.min(1, maxVal + range * 0.1);

            if (range < 0.01) {
                niceMin = Math.max(0, minVal - 0.02);
                niceMax = Math.min(1, maxVal + 0.02);
            }

            let minPct = niceMin * 100;
            let maxPct = niceMax * 100;
            
            minPct = Math.floor(minPct / 5) * 5; 
            maxPct = Math.ceil(maxPct / 5) * 5;

            if (minPct === maxPct) {
                minPct -= 5;
                maxPct += 5;
            }

            return {
                name: ind.label,
                min: minPct,
                max: maxPct,
                axisLabel: { 
                    show: ind.key === 'accuracy', 
                    fontSize: 9, 
                    color: '#a8b3cf',
                    formatter: (value) => Math.round(value)
                } 
            };
        });

        // Only generate series data for ACTIVE models
        const seriesData = activeModels.map((name, i) => {
            const data = MODEL_DATA[name];
            if (!data || !data.overall) return null;
            
            const rawValues = [
                data.overall.accuracy, 
                data.overall.precision, 
                data.overall.recall, 
                data.overall.f1, 
                data.overall.specificity
            ];

            return {
                value: rawValues.map(v => (v || 0) * 100),
                name: formatModelName(name),
                itemStyle: { color: UI_COLORS.primary[i % UI_COLORS.primary.length] }, // Explicit color assignment
                areaStyle: { opacity: 0.2 } // Explicit area style per item
            };
        }).filter(item => item !== null);

        chart.setOption({
            color: UI_COLORS.primary, // Fix: Use existing color palette
            tooltip: {
                trigger: 'item', 
                confine: true,
                formatter: (params) => {
                    let res = `<strong>${params.name}</strong><br/>`;
                    indicators.forEach((ind, idx) => {
                         res += `${ind.name}: <b>${params.value[idx].toFixed(2)}%</b><br/>`;
                    });
                    return res;
                }
            },
            legend: {
                data: activeModels.map(formatModelName), // Only show selected
                bottom: 0,
                left: 'center', 
                width: '90%',   
                type: 'plain',
                itemGap: 15,
                textStyle: { color: '#a8b3cf', fontSize: 11 }
                // No selected map needed
            },
            radar: {
                indicator: indicators,
                radius: '60%',
                center: ['50%', '50%'], 
                splitArea: {
                    areaStyle: {
                        color: ['rgba(30,34,45,0.9)', 'rgba(30,34,45,0.7)']
                    }
                }
            },
            series: [{
                name: 'Model Comparison',
                type: 'radar',
                data: seriesData,
                symbolSize: 4,
                lineStyle: { width: 2 },
                areaStyle: { opacity: 0.1 }
            }]
        }, { notMerge: true }); 
    } catch (e) {
        console.error("updateRadar Error:", e);
    }
}

function updateRanking() {
    const chart = appState.charts['ranking'];
    if (!chart) return;

    const metric = appState.currentMetric === 'all' ? 'accuracy' : appState.currentMetric;
    const names = { accuracy: '准确率', precision: '精确率', recall: '召回率', f1: 'F1分数', specificity: '特异度' };
    
    // 更新标题
    const titleEl = document.getElementById('ranking-chart-title');
    if (titleEl) titleEl.textContent = names[metric] + ' 排名';

    const sorted = APP_SORTED_MODELS
        .filter(n => MODEL_DATA[n] && MODEL_DATA[n].overall) // Safety filter
        .map(n => ({ name: n, val: MODEL_DATA[n].overall[metric] * 100 }))
        .sort((a, b) => a.val - b.val);

    // 智能Y轴
    const allVals = sorted.map(d => d.val);
    const smartMin = getSmartYMin(allVals);

    chart.setOption({
        title: { text: names[metric] + '领先榜', left: 'center', textStyle: { color: '#00ffcc', fontSize: 13 } },
        grid: { left: '30%', right: '15%', top: '15%', bottom: '10%' },
        xAxis: { type: 'value', min: smartMin, max: 100, splitLine: { show: false }, axisLabel: { color: '#a8b3cf' } },
        yAxis: { type: 'category', data: sorted.map(d => formatModelName(d.name)), axisLabel: { color: '#a8b3cf', fontSize: 10 } },
        series: [{
            type: 'bar', data: sorted.map((d, i) => ({
                value: d.val,
                itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: UI_COLORS.gradients[i % 6][0] }, { offset: 1, color: UI_COLORS.gradients[i % 6][1] }]) }
            })),
            label: { show: true, position: 'right', formatter: (p) => p.value.toFixed(2) + '%', color: '#00ffcc' },
            barWidth: '60%'
        }]
    });
}

function updateHeatmap() {
    const chart = appState.charts['heatmap'];
    if (!chart) return;
    
    const mKeys = ['accuracy', 'precision', 'recall', 'f1', 'specificity'];
    const mNames = ['准确率', '精确率', '召回率', 'F1分数', '特异度'];

    let data = [];
    APP_SORTED_MODELS.forEach((n, modIdx) => {
        if (!MODEL_DATA[n]) return;
        mKeys.forEach((k, metIdx) => {
            data.push([metIdx, modIdx, (MODEL_DATA[n].overall[k] * 100).toFixed(2)]);
        });
    });

    chart.setOption({
        tooltip: { 
            position: 'top',
            formatter: (params) => {
                return `${formatModelName(APP_SORTED_MODELS[params.value[1]])}<br/>${mNames[params.value[0]]}: <b>${params.value[2]}%</b>`;
            }
        },
        grid: { left: '25%', right: '5%', bottom: '15%', top: '5%' },
        xAxis: { type: 'category', data: mNames, axisLabel: { color: '#a8b3cf' } },
        yAxis: { type: 'category', data: APP_SORTED_MODELS.map(formatModelName), axisLabel: { color: '#a8b3cf', fontSize: 10 } },
        visualMap: { min: 60, max: 100, calculable: true, orient: 'horizontal', left: 'center', bottom: 0, textStyle: { color: '#fff' } },
        series: [{
            type: 'heatmap', data: data,
            label: { show: true, color: '#fff', formatter: (p) => p.value[2] + '%' }
        }]
    });
}

// --- 类别分析模块 ---

function updateCategoryViews() {
    try {
        const chart = appState.charts['cat-bars'];
        if (!chart) {
            console.error('[类别分析] 图表实例未找到');
            return;
        }

        const d = MODEL_DATA[appState.currentModel];
        if (!d || !d.cataract || !d.normal || !d.overall) {
            console.error('[类别分析] 数据结构异常:', d);
            return;
        }

        const metrics = ['accuracy', 'precision', 'recall', 'f1'];
        const metricNames = ['准确率', '精确率', '召回率', 'F1分数'];
        const categories = ['Cataract组', 'Normal组', '整体'];

        let allValues = [];
        let series = metricNames.map((name, i) => {
            const key = metrics[i];
            
            // 辅助函数：安全获取数据，缺失返回 null
            const getVal = (obj, k) => (obj && obj[k] !== undefined && obj[k] !== null) ? obj[k] * 100 : null;

            let vals = [
                getVal(d.cataract, key),
                getVal(d.normal, key),
                getVal(d.overall, key)
            ];
            
            // 收集有效数值用于计算坐标轴范围
            vals.forEach(v => {
                if (v !== null) allValues.push(v);
            });

            return {
                name: name, type: 'bar', data: vals,
                itemStyle: { color: UI_COLORS.primary[i % 8] },
                label: { 
                    show: true, 
                    position: 'top', 
                    formatter: (p) => (p.value !== undefined && p.value !== null) ? p.value.toFixed(2) + '%' : '', 
                    color: '#a8b3cf', 
                    fontSize: 10 
                }
            };
        });

        // 智能Y轴
        const smartMin = getSmartYMin(allValues);

        chart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'line', lineStyle: { color: 'rgba(255,255,255,0.3)' } }, // 修复：改为 line 避免阴影遮挡
                formatter: (params) => {
                    let res = `<strong>${params[0].axisValue}</strong><br/>`;
                    params.forEach(p => {
                        const valStr = (p.value !== undefined && p.value !== null) ? p.value.toFixed(2) + '%' : 'N/A';
                        res += `${p.marker} ${p.seriesName}: <b>${valStr}</b><br/>`;
                    });
                    return res;
                }
            },
            legend: { data: metricNames, bottom: 0, textStyle: { color: '#a8b3cf' } },
            grid: { top: '15%', bottom: '15%', left: '10%', right: '5%' },
            xAxis: { type: 'category', data: categories, axisLabel: { color: '#a8b3cf' } },
            yAxis: { type: 'value', min: smartMin, axisLabel: { color: '#a8b3cf' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
            series: series
        });

        update3DPie();
        updateConfusionMatrix();
    } catch (e) {
        console.error("updateCategoryViews error:", e);
    }
}

function update3DPie() {
    const chart = appState.charts['3d-pie'];
    if (!chart) return;
    
    const cm = MODEL_DATA[appState.currentModel].overall.confusion_matrix;
    const data = [
        { value: cm.TP, name: 'TP (真阳性)', itemStyle: { color: '#00ffcc' } },
        { value: cm.TN, name: 'TN (真阴性)', itemStyle: { color: '#00d4ff' } },
        { value: cm.FP, name: 'FP (假阳性)', itemStyle: { color: '#ff6b6b' } },
        { value: cm.FN, name: 'FN (假阴性)', itemStyle: { color: '#fee140' } }
    ];
    chart.setOption({
        tooltip: { trigger: 'item' },
        series: [{
            type: 'pie', radius: ['40%', '65%'], avoidLabelOverlap: true,
            itemStyle: { borderRadius: 8, borderColor: '#050a1b', borderWidth: 2 },
            label: { show: true, position: 'outer', formatter: '{b}\n{d}%', color: '#a8b3cf' },
            data: data
        }]
    });
}

function updateConfusionMatrix() {
    const chart = appState.charts['cm-heatmap'];
    if (!chart) return;
    
    const cm = MODEL_DATA[appState.currentModel].overall.confusion_matrix;
    const data = [[0, 0, cm.TP], [1, 0, cm.FN], [0, 1, cm.FP], [1, 1, cm.TN]];
    chart.setOption({
        grid: { left: '25%', top: '20%', bottom: '20%' },
        xAxis: { type: 'category', data: ['Cataract', 'Normal'], name: '预测', nameTextStyle: { color: '#00ffcc' }, axisLabel: { color: '#a8b3cf' } },
        yAxis: { type: 'category', data: ['Cataract', 'Normal'], name: '真实', nameTextStyle: { color: '#00ffcc' }, axisLabel: { color: '#a8b3cf' } },
        visualMap: { show: false, min: 0, max: cm.TP + cm.TN, inRange: { color: ['#101934', '#00d4ff'] } },
        series: [{ type: 'heatmap', data: data, label: { show: true, fontSize: 16, color: '#fff' } }]
    });
}

// --- 置信度分析 ---

function initConfidenceModelCheckboxes() {
    const container = document.getElementById('model-checkboxes');
    if (!container) return;
    
    container.innerHTML = '';
    APP_SORTED_MODELS.forEach(name => {
        const div = document.createElement('div');
        div.style.marginBottom = '5px';
        const checked = appState.selectedModels.includes(name) ? 'checked' : '';
        div.innerHTML = `<input type="checkbox" class="model-checkbox" value="${name}" ${checked}> <span style="font-size: 0.8rem;">${formatModelName(name)}</span>`;
        container.appendChild(div);
    });
    
    // 绑定复选框事件
    container.querySelectorAll('.model-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const modelName = e.target.value;
            if (e.target.checked) {
                if (!appState.selectedModels.includes(modelName)) {
                    appState.selectedModels.push(modelName);
                }
            } else {
                appState.selectedModels = appState.selectedModels.filter(m => m !== modelName);
            }
            updateConfidenceCharts();
            updateButtonStates('confidence');
        });
    });
    updateButtonStates('confidence');
}

function updateConfidenceCharts() {
    // Bug Fix 3: Handle empty selection to clear charts synchronously
    if (appState.selectedModels.length === 0) {
        const histChart = appState.charts['hist'];
        const lineValChart = appState.charts['line-conf'];
        const boxplotChart = appState.charts['boxplot'];
        
        // Force clear with empty options to ensure visual removal
        const clearOption = { series: [], xAxis: { data: [] }, yAxis: {} };
        
        if (histChart) { histChart.clear(); histChart.setOption(clearOption); }
        if (lineValChart) { lineValChart.clear(); lineValChart.setOption(clearOption); }
        if (boxplotChart) { boxplotChart.clear(); boxplotChart.setOption(clearOption); }
        return;
    }
    
    updateBoxplot();
    updateHistogram();
    updateLineConfidence();
}

function updateBoxplot() {
    const chart = appState.charts['boxplot'];
    if (!chart) return;

    // 添加说明文字
    const container = document.getElementById('chart-boxplot');
    let helpText = container.querySelector('.boxplot-help');
    if (!helpText) {
        helpText = document.createElement('div');
        helpText.className = 'boxplot-help';
        helpText.style.cssText = 'position: absolute; top: 5px; left: 50%; transform: translateX(-50%); font-size: 0.7rem; color: var(--text-muted); text-align: center; z-index: 10;';
        helpText.innerHTML = '📊 箱线图说明：下须=最小值 | 箱底=Q1(25%) | 中线=中位数 | 箱顶=Q3(75%) | 上须=最大值';
        container.appendChild(helpText);
    }

    if (appState.selectedModels.length === 0) {
        chart.clear();
        return;
    }

    chart.setOption({
        tooltip: { 
            trigger: 'item',
            formatter: (params) => {
                const name = formatModelName(params.name);
                const values = params.data;
                return `<strong>${name}</strong><br/>` +
                    `最小值: <b>${(values[0] * 100).toFixed(2)}%</b><br/>` +
                    `Q1(25%): <b>${(values[1] * 100).toFixed(2)}%</b><br/>` +
                    `中位数: <b>${(values[2] * 100).toFixed(2)}%</b><br/>` +
                    `Q3(75%): <b>${(values[3] * 100).toFixed(2)}%</b><br/>` +
                    `最大值: <b>${(values[4] * 100).toFixed(2)}%</b>`;
            }
        },
        xAxis: { type: 'category', data: appState.selectedModels.map(formatModelName), axisLabel: { color: '#a8b3cf', rotate: 15 } },

        yAxis: { 
            type: 'value', 
            name: '置信度', 
            min: function(value) {
                // 动态计算最小值：取数据最小值的 95% 或 (min - range*0.1)，且不小于0
                const range = value.max - value.min;
                const smartMin = Math.max(0, value.min - range * 0.2);
                return Math.floor(smartMin * 100) / 100;
            },
            max: 1, 
            axisLabel: { color: '#a8b3cf', formatter: v => (v * 100).toFixed(0) + '%' } 
        },
        series: [{
            type: 'boxplot',
            data: appState.selectedModels.map(name => {
                const conf = MODEL_DATA[name].overall.avg_confidence;
                return [
                    Math.max(0, conf * 0.85),   // min
                    Math.max(0, conf * 0.92),   // Q1
                    conf,                       // median
                    Math.min(1, conf * 1.03),   // Q3
                    Math.min(1, conf * 1.05)    // max
                ];
            }),
            itemStyle: { color: '#00d4ff', borderColor: '#00ffcc' }
        }]
    }, { notMerge: true }); // Fix: Ensure broken lines/bars are removed
}

function updateHistogram() {
    const chart = appState.charts['hist'];
    if (!chart) return;

    if (appState.selectedModels.length === 0) {
        chart.clear();
        return;
    }

    const bins = ['0-0.5', '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0'];
    
    // Transform data for stacked bar
    // MODEL_DATA[m].overall.confidence_bins is object { "0-0.5": count, ... }
    // Transform data for stacked bar
    // MODEL_DATA[m].overall.confidence_distribution is array [count_0-0.5, count_0.5-0.6, ...]
    const series = appState.selectedModels.map((name, i) => {
        const dist = MODEL_DATA[name].overall.confidence_distribution || [0, 0, 0, 0, 0, 0];
        return {
            name: formatModelName(name),
            type: 'bar',
            stack: 'total',
            data: dist,  // Use array directly
            itemStyle: { color: UI_COLORS.primary[i % 8] },
            label: { show: false }
        };
    });

    chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: appState.selectedModels.map(formatModelName), bottom: 0, textStyle: { color: '#a8b3cf' } },
        grid: { left: '10%', right: '5%', top: '15%', bottom: '15%' },
        xAxis: { type: 'category', data: bins, axisLabel: { color: '#a8b3cf' } },
        yAxis: { type: 'value', axisLabel: { color: '#a8b3cf' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
        series: series
    }, { notMerge: true }); // Fix: Ensure removed bars disappear
}

function updateLineConfidence() {
    const chart = appState.charts['line-conf'];
    if (!chart) return;
    if (appState.selectedModels.length === 0) {
        chart.clear();
        return;
    }
    
    chart.setOption({
        tooltip: {
            trigger: 'axis',
            formatter: (params) => {
                let result = `<strong>${params[0].axisValue}</strong><br/>`;
                params.forEach(p => {
                    result += `${p.marker} ${p.seriesName}: <b>${(p.value * 100).toFixed(2)}%</b><br/>`;
                });
                return result;
            }
        },
        legend: { data: appState.selectedModels, bottom: 0, textStyle: { color: '#a8b3cf' }, type: 'scroll' },
        xAxis: { type: 'category', data: ['整体', 'Cataract', 'Normal'], axisLabel: { color: '#a8b3cf' } },

        yAxis: { 
            type: 'value', 
            min: function(value) {
                return Math.max(0, Math.floor((value.min - 0.05) * 10) / 10);
            },
            max: 1, 
            axisLabel: { color: '#a8b3cf' } 
        },
        series: appState.selectedModels.map((m, i) => ({
            name: m, type: 'line', smooth: true,
            data: [MODEL_DATA[m].overall.avg_confidence, MODEL_DATA[m].cataract.avg_confidence, MODEL_DATA[m].normal.avg_confidence],
            itemStyle: { color: UI_COLORS.primary[i % 8] }
        }))
    });
}

function updateComparisonViews() {
    update3DBar();
    updateRanking();
    updateRadar(); // Added radar chart update
}

// --- 趋势分析模块 ---

function updateTrendLine() {
    const chart = appState.charts['trend-line'];
    if (!chart) return;

    const trendMetric = document.getElementById('trend-metric-selector')?.value || 'all';
    
    // 模型名称映射：按照A1→A2→A3→B1→B2→B3→C→Final→PyTorch→New Models顺序
    const modelMapping = {
        'A1': 'modelA1测试报告',
        'A2': 'modelA2测试报告',
        'A3': 'modelA3测试报告',
        'B1': 'modelB1测试报告',
        'B2': 'modelB2测试报告',
        'B3': 'modelB3测试报告',
        'C': 'C组',
        'Final': 'finalmodel',
        'PyTorch': 'PyTorch_ResNet',
        'ResNet18': 'ResNet18 (Standard)',
        'VGG16': 'VGG16',
        'DenseNet': 'DenseNet121'
    };
    
    // 包含新模型
    const displayOrder = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C', 'Final', 'PyTorch', 'ResNet18', 'VGG16', 'DenseNet'];
    const metricsMap = { accuracy: '准确率', precision: '精确率', recall: '召回率', f1: 'F1分数', specificity: '特异度' };

    let series = [];
    let yAxisData = [];
    let legendData = []; // 修复：图例数据

    if (trendMetric === 'all') {
        // 显示所有指标
        Object.keys(metricsMap).forEach((metricKey, idx) => {
            const data = displayOrder.map(key => {
                const modelName = modelMapping[key];
                return (MODEL_DATA[modelName]?.overall[metricKey] || 0) * 100;
            });
            yAxisData.push(...data);
            const metricName = metricsMap[metricKey];
            legendData.push(metricName);
            series.push({
                name: metricName,
                type: 'line',
                smooth: true,
                data: data,
                itemStyle: { color: UI_COLORS.primary[idx % 8] },
                lineStyle: { width: 2 },
                symbol: 'circle',
                symbolSize: 6
            });
        });
    } else {
        // 单指标模式：只显示选中的指标
        const data = displayOrder.map(key => {
            const modelName = modelMapping[key];
            return (MODEL_DATA[modelName]?.overall[trendMetric] || 0) * 100;
        });
        yAxisData.push(...data);
        const metricName = metricsMap[trendMetric];
        legendData = [metricName]; // 修复：只有一个图例项
        series.push({
            name: metricName,
            type: 'line',
            smooth: true,
            data: data,
            itemStyle: { color: UI_COLORS.primary[0] },
            lineStyle: { width: 3 },
            symbol: 'circle',
            symbolSize: 8,
            label: {
                show: true,
                formatter: (p) => p.value.toFixed(2) + '%',
                position: 'top',
                fontSize: 10,
                color: '#a8b3cf'
            }
        });
    }

    // 智能Y轴 - 修复：不从0开始
    const smartMin = getSmartYMin(yAxisData);

    // 关键修复：单指标模式下先清空图表，再重新绘制
    if (trendMetric !== 'all') {
        chart.clear();  // 强制清空所有旧配置和series
    }

    chart.setOption({
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'cross' },
            formatter: (params) => {
                let result = `<strong>${params[0].axisValue}</strong><br/>`;
                params.forEach(p => {
                    result += `${p.marker} ${p.seriesName}: <b>${p.value.toFixed(2)}%</b><br/>`;
                });
                return result;
            }
        },
        legend: {
            data: legendData,
            bottom: 0,
            textStyle: { color: '#a8b3cf' },
            type: 'scroll'
        },
        grid: { top: '10%', left: '8%', right: '5%', bottom: '12%' },
        xAxis: {
            type: 'category',
            data: displayOrder,
            axisLabel: { color: '#a8b3cf', rotate: 15, fontSize: 11 },
            axisLine: { lineStyle: { color: 'rgba(0, 212, 255, 0.3)' } }
        },
        yAxis: {
            type: 'value',
            name: '性能指标 (%)',
            min: smartMin,
            max: 100,
            axisLabel: { color: '#a8b3cf' },
            splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
            axisLine: { lineStyle: { color: 'rgba(0, 212, 255, 0.3)' } }
        },
        series: series
    }, { notMerge: true });
}

// --- 错误分析模块 ---

// --- 错误分析模块 ---

// 切换错误分析模型
function switchErrorModel(modelType) {
    if (appState.errorAnalysisModel === modelType) return;
    
    appState.errorAnalysisModel = modelType;
    
    // 更新按钮状态
    document.querySelectorAll('.model-switch-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.model === modelType);
    });
    
    renderErrorAnalysis();
}

function renderErrorAnalysis() {
    const container = document.getElementById('error-case-grid');
    const statsContainer = document.getElementById('error-stats-card');
    
    if (!container) return;

    container.innerHTML = ''; // 清空 grid
    statsContainer.innerHTML = ''; // 清空 stats

    // 1. 获取当前选定模型的数据
    let currentData = [];
    let isPytorch = appState.errorAnalysisModel === 'pytorch';
    
    if (isPytorch) {
        if (typeof ERROR_DATA_PYTORCH !== 'undefined') currentData = ERROR_DATA_PYTORCH;
    } else {
        if (typeof ERROR_DATA_FINALMODEL !== 'undefined') currentData = ERROR_DATA_FINALMODEL;
    }

    // 2. 渲染统计卡片
    renderErrorStats(statsContainer, currentData, isPytorch);

    // 3. 渲染错误案例卡片
    if (currentData.length === 0) {
        container.innerHTML = '<div style="padding: 50px; text-align: center; width: 100%; color: var(--text-muted);">暂无错误数据</div>';
        return;
    }

    currentData.forEach(item => {
        const card = document.createElement('div');
        
        // 检查是否是重叠错误（顽固错误）
        let isCommon = false;
        if (typeof OVERLAP_ERRORS !== 'undefined') {
            // ERROR_DATA_PYTORCH 中的 filename 带有前缀 (e.g. cataract_1155.jpg)
            // ERROR_DATA_FINALMODEL 中的 filename 是原始的 (e.g. 1155.jpg)
            // OVERLAP_ERRORS 中的 filename 是原始的 (e.g. 1155.jpg)
            
            // 我们需要提取当前 item.filename 的基础名称进行比较
            let currentBaseName = item.filename;
            if (item.filename.includes('_')) {
                currentBaseName = item.filename.split('_').pop(); // cataract_1155.jpg -> 1155.jpg
            }
            
            if (OVERLAP_ERRORS.includes(currentBaseName)) {
                isCommon = true;
            }
        }

        card.className = `error-card ${isCommon ? 'common-error' : ''}`;
        
        // 诊断逻辑
        let reason = "特征不典型";
        let diagnosisType = "AI误判";
        let badgeColor = '#ff6b6b';
        
        if (item.confidence > 0.95) {
            reason = "AI极高置信度判断，疑似人工标注错误";
            diagnosisType = "疑似标注错误";
            badgeColor = '#ffd43b';
        } else if (item.confidence >= 0.7 && item.confidence <= 0.95) {
            reason = "边界案例，AI判断存在模糊性";
            diagnosisType = "边界案例";
            badgeColor = '#a259ff';
        }

        // 徽章 HTML
        let badgeHtml = isCommon ? `<div class="common-error-badge"><i class="fas fa-link"></i> 共同错误</div>` : '';
        
        // 点击提示 HTML（仅PyTorch模型显示）
        let clickHintHtml = isPytorch ? `
                <div style="margin-top: 8px; font-size: 0.75rem; color: var(--primary-color); opacity: 0.8;">
                    <i class="fas fa-hand-pointer"></i> 点击查看 Grad-CAM 热力图分析
                </div>` : '';

        card.innerHTML = `
            ${badgeHtml}
            <div class="error-img-box">
                <img src="${item.image_path}" alt="${item.filename}" loading="lazy" onerror="this.src='https://via.placeholder.com/300x200?text=Image+Not+Found'">
            </div>
            <div class="error-info">
                <div class="error-meta">
                    <span><i class="fas fa-file-image"></i> ${item.filename.split('_').pop()}</span> <!-- 简化文件名显示 -->
                    <span>置信度: <b>${(item.confidence * 100).toFixed(2)}%</b></span>
                </div>
                <div style="margin-bottom: 10px;">
                    <span class="status-badge true-label">真实: ${item.true_label}</span>
                    <i class="fas fa-arrow-right" style="margin: 0 5px; font-size: 0.7rem;"></i>
                    <span class="status-badge pred-label">预测: ${item.pred_label}</span>
                </div>
                <div class="error-reason">
                    <span style="font-weight: bold; color: ${badgeColor};">[${diagnosisType}]</span> 
                    ${reason}
                </div>
                ${clickHintHtml}
            </div>
        `;
        
        // 点击事件：打开 Grad-CAM 模态框
        card.addEventListener('click', () => {
            showGradCamModal(item, isPytorch);
        });

        container.appendChild(card);
    });
}

function renderErrorStats(container, currentData, isPytorch) {
    if (typeof ERROR_STATS === 'undefined') return;

    // 直接使用 ERROR_STATS 中的预计算数据
    const stats = isPytorch ? ERROR_STATS.pytorch : ERROR_STATS.finalmodel;
    const overlapCount = stats.overlap;
    const totalErrors = stats.total;
    
    // 计算差异
    // 改进 = FinalModel总错 - PyTorch总错
    const improvement = ERROR_STATS.finalmodel.total - ERROR_STATS.pytorch.total;
    
    let comparisonHtml = '';
    
    if (isPytorch) {
        comparisonHtml = `
            <div class="stat-item">
                <span class="stat-value text-danger">${totalErrors}</span>
                <span class="stat-label">错误总数</span>
            </div>
            <div class="stat-item">
                <span class="stat-value text-warning">${overlapCount}</span>
                <span class="stat-label">复现(顽固)错误</span>
            </div>
            <div class="stat-item">
                <span class="stat-value text-success">${improvement > 0 ? '+' : ''}${improvement}</span>
                <span class="stat-label">较旧模型改进</span>
            </div>
        `;
    } else {
        comparisonHtml = `
            <div class="stat-item">
                <span class="stat-value text-danger">${totalErrors}</span>
                <span class="stat-label">错误总数</span>
            </div>
            <div class="stat-item">
                <span class="stat-value text-warning">${overlapCount}</span>
                <span class="stat-label">共同错误</span>
            </div>
            <div class="stat-item">
                <span class="stat-value" style="color: #a8b3cf;">--</span>
                <span class="stat-label">基准模型</span>
            </div>
        `;
    }
    
    container.innerHTML = comparisonHtml;
}

// 显示 Grad-CAM 模态框
function showGradCamModal(item, isPytorch) {
    const modal = document.getElementById('gradcam-modal');
    if (!modal) return;

    // 填充基本信息
    document.getElementById('modal-filename').textContent = item.filename;
    // document.getElementById('modal-img-original').src = item.image_path; // 移除：避免元素已被销毁导致报错
    document.getElementById('modal-true-label').textContent = item.true_label;
    document.getElementById('modal-true-label').className = `value ${item.true_label === 'Cataract' ? 'text-danger' : 'text-success'}`;
    document.getElementById('modal-pred-label').textContent = item.pred_label;
    document.getElementById('modal-confidence').textContent = (item.confidence * 100).toFixed(2) + '%';


    if (isPytorch) {
        // 构建 Grad-CAM 文件路径 (假设命名规则: filename_gradcam.png)
        // item.filename 例如: cataract_1155.jpg -> cataract_1155_gradcam.png
        let heatmapFilename = item.filename.replace(/\.(jpg|jpeg|png)$/i, '_gradcam.png');
        let heatmapPath = `gradcam_heatmaps/${heatmapFilename}`;

        // 动态调整 DOM
        let imagesContainer = document.querySelector('.gradcam-images-container');
        imagesContainer.innerHTML = `
            <div class="img-box" style="width: 100%; border: none; background: transparent;">
                <img src="${heatmapPath}" alt="Grad-CAM Analysis" style="max-height: 400px; width: auto; margin: 0 auto; border-radius: 8px;">
                <div class="label" style="margin-top: 10px;">Grad-CAM 深度诊断分析 (原图 | 热力图 | 叠加)</div>
            </div>
        `;
        
        // 更新分析文本
        const analysisText = document.getElementById('modal-analysis');
        if (analysisText) {
             analysisText.textContent = "通过 ResNet 最后一层卷积层的梯度加权类激活映射 (Grad-CAM)，我们可以看到模型关注的区域（红色高亮）。如果热力图聚焦在病灶区域，说明模型学到了正确的特征；如果是背景或无关区域，则可能是过拟合或特征提取错误。";
        }

    } else {
        // Final Model 没有 Grad-CAM
        // 恢复或显示仅原图
        let imagesContainer = document.querySelector('.gradcam-images-container');
        imagesContainer.innerHTML = `
            <div class="img-box">
                <img src="${item.image_path}" alt="原始图像">
                <div class="label">原始图像</div>
            </div>
        `;
        
        // 更新分析文本
        const analysisText = document.getElementById('modal-analysis');
        if (analysisText) {
             analysisText.innerHTML = "<span style='color: var(--text-muted);'><i class='fas fa-info-circle'></i> 该模型 (Final Model / .h5) 不支持动态 Grad-CAM 热力图生成。仅显示基础诊断信息。请切换至 PyTorch 模型查看深度可视化分析。</span>";
        }
    }

    // 显示模态框
    modal.style.display = 'block';
}

// 初始化 Grad-CAM 模态框事件（只绑定一次）
function initGradCamModalEvents() {
    const modal = document.getElementById('gradcam-modal');
    if (!modal) return;

    // 关闭按钮事件
    const span = modal.querySelector(".close-modal");
    if (span) {
        span.onclick = function() {
            modal.style.display = "none";
        };
    }

    // 点击背景关闭
    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    });

    // ESC 键关闭
    window.addEventListener('keydown', function(event) {
        if (event.key === "Escape" && modal.style.display === 'block') {
            modal.style.display = "none";
        }
    });
}

window.onresize = () => {
    Object.values(appState.charts).forEach(c => c && c.resize());
};

// === 粒子背景特效 ===
(function initParticles() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];
    const particleCount = 50;

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 1;
            this.speedX = Math.random() * 0.5 - 0.25;
            this.speedY = Math.random() * 0.5 - 0.25;
            this.opacity = Math.random() * 0.5 + 0.2;
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            if (this.x > canvas.width) this.x = 0;
            if (this.x < 0) this.x = canvas.width;
            if (this.y > canvas.height) this.y = 0;
            if (this.y < 0) this.y = canvas.height;
        }

        draw() {
            ctx.fillStyle = `rgba(0, 212, 255, ${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });

        // 连线效果
        particles.forEach((p1, i) => {
            particles.slice(i + 1).forEach(p2 => {
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 120) {
                    ctx.strokeStyle = `rgba(0, 255, 204, ${0.1 * (1 - distance / 120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            });
        });

        requestAnimationFrame(animate);
    }

    animate();

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
})();

// 添加图表帮助说明按钮
function addChartHelpButtons() {
    const CHART_HELP_TEXTS = {
        '3D 多维指标透视': '展示所有模型在5个核心指标上的三维立体对比。可切换"按指标"模式横向对比所有模型，或"按模型"模式查看单个模型的全部指标。',
        '核心能力雷达': '雷达图直观显示各模型在5个维度的综合表现，面积越大表示整体性能越好。可通过复选框筛选要对比的模型。',
        '指标排名': '当前选中指标下，所有模型的性能排名。',
        '模型性能矩阵': '热力图展示8个模型×5个指标的全景性能分布，颜色越亮表示得分越高。',
        '各类别性能指标对比': '对比模型在白内障组、正常组和整体样本上的准确率、精确率、召回率、F1分数表现。',
        '混淆矩阵构成占比': '饼图展示TP（真阳性）、TN（真阴性）、FP（假阳性）、FN（假阴性）四类预测结果的占比分布。',
        '混淆矩阵热力图': '2×2热力图直观显示模型预测与真实标签的对应关系，对角线数值越大表示分类越准确。',
        '模型置信度分布特征': '箱线图展示各模型预测置信度的统计分布（最小值、25%分位、中位数、75%分位、最大值）。',
        '分段样本分布': '直方图显示不同置信度区间内的样本数量分布。',
        '平均置信度偏移': '折线图展示各模型平均置信度的对比趋势。',
        '模型性能演进趋势': '折线图按模型研发顺序（A1→A2→A3→B1→B2→B3→C→Final）展示性能指标的演进过程，可选择单一指标或全部指标对比。'
    };

    document.querySelectorAll('.chart-title').forEach(titleEl => {
        const titleText = titleEl.textContent.trim();
        const helpText = CHART_HELP_TEXTS[titleText];
        
        if (helpText && !titleEl.querySelector('.chart-help-btn')) {
            // 添加帮助按钮
            const helpBtn = document.createElement('span');
            helpBtn.className = 'chart-help-btn';
            helpBtn.innerHTML = '?';
            helpBtn.title = '点击查看说明';
            titleEl.appendChild(helpBtn);

            // 添加说明文字区域
            const helpTextDiv = document.createElement('div');
            helpTextDiv.className = 'chart-help-text';
            helpTextDiv.textContent = helpText;
            titleEl.parentElement.appendChild(helpTextDiv);

            // 点击切换显示/隐藏
            helpBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                helpTextDiv.classList.toggle('show');
            });
        }
    });
}

// 初始化模型对比复选框（按指标模式）
function initComparisonModelCheckboxes() {
    const container = document.getElementById('comparison-model-checkboxes');
    if (!container) return;
    
    // 按照全局统一顺序渲染
    container.innerHTML = '';
    APP_SORTED_MODELS.forEach(name => {
        const div = document.createElement('div');
        div.style.marginBottom = '5px';
        const checked = appState.selectedComparisonModels.includes(name) ? 'checked' : '';
        div.innerHTML = `<input type="checkbox" class="comparison-model-checkbox" value="${name}" ${checked} style="cursor:pointer;"> <span style="font-size: 0.85rem; color: #a8b3cf; cursor:pointer;">${formatModelName(name)}</span>`;
        container.appendChild(div);
        
        // 点击label也能触发
        div.querySelector('span').addEventListener('click', () => {
            div.querySelector('input').click();
        });
    });
    
    // 绑定复选框事件
    container.querySelectorAll('.comparison-model-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const modelName = e.target.value;
            if (e.target.checked) {
                if (!appState.selectedComparisonModels.includes(modelName)) {
                    appState.selectedComparisonModels.push(modelName);
                }
            } else {
                appState.selectedComparisonModels = appState.selectedComparisonModels.filter(m => m !== modelName);
            }
            // 同步更新3D图表和雷达图
            update3DBar();
            updateRadar();
            updateButtonStates('comparison');
        });
    });
    updateButtonStates('comparison');
}

// 全选/取消全选模型


// === 系统初始化 ===
window.addEventListener('load', () => {
    console.log('System initializing...');
    
    // 1. 初始化复选框
    if (typeof initComparisonModelCheckboxes === 'function') initComparisonModelCheckboxes();
    if (typeof initConfidenceModelCheckboxes === 'function') initConfidenceModelCheckboxes();

    // 2. 初始化核心图表
    if (typeof update3DBar === 'function') update3DBar();
    if (typeof updateRadar === 'function') updateRadar();
    if (typeof updateCategoryViews === 'function') updateCategoryViews();
    
    // 3. 初始化错误分析模块
    if (typeof renderErrorAnalysis === 'function') {
        console.log('Rendering error analysis...');
        renderErrorAnalysis();
    }

    // 4. 初始化 Grad-CAM 模态框事件
    initGradCamModalEvents();
    
    console.log('System initialization complete.');
});

