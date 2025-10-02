import React, {useEffect, useRef} from 'react';

// ПЕРЕИМЕНОВАЛ КОМПОНЕНТ - важно!
const SimpleGraph = ({data, type = 'line', title = '', color = '#007bff'}) => {
    const chartRef = useRef(null);
    const chartInstance = useRef(null);

    useEffect(() => {
        // Динамический импорт чтобы избежать конфликтов
        const initChart = async () => {
            if (!chartRef.current || !data || Object.keys(data).length === 0) return;

            try {
                const {Chart, registerables} = await import('chart.js');
                Chart.register(...registerables);

                const ctx = chartRef.current.getContext('2d');

                // Уничтожаем старый график
                if (chartInstance.current) {
                    chartInstance.current.destroy();
                }

                // Создаём новый график
                chartInstance.current = new Chart(ctx, {
                    type: type,
                    data: {
                        labels: Object.keys(data),
                        datasets: [{
                            label: title,
                            data: Object.values(data),
                            borderColor: color,
                            backgroundColor: type === 'bar' ? color : `${color}33`,
                            borderWidth: 2,
                            tension: type === 'line' ? 0.1 : 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: !!title,
                                text: title
                            },
                            legend: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });

            } catch (error) {
                console.error('Ошибка инициализации графика:', error);
            }
        };

        initChart();

        return () => {
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, [data, type, title, color]);

    if (!data || Object.keys(data).length === 0) {
        return (
            <div style={{
                padding: '20px',
                textAlign: 'center',
                border: '1px dashed #ccc',
                borderRadius: '4px'
            }}>
                Нет данных для графика
            </div>
        );
    }

    return (
        <div style={{position: 'relative', height: '400px', width: '100%'}}>
            <canvas ref={chartRef}/>
        </div>
    );
};

export default SimpleGraph;