import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';

interface PlotlyChartProps {
  data: Plotly.Data[];
  layout?: Partial<Plotly.Layout>;
  config?: Partial<Plotly.Config>;
  className?: string;
  style?: React.CSSProperties;
}

export const PlotlyChart: React.FC<PlotlyChartProps> = ({
  data,
  layout = {},
  config = {},
  className = '',
  style = { height: '100%', width: '100%' },
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const darkDefaults: Partial<Plotly.Layout> = {
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {
        family: 'Inter, system-ui, sans-serif',
        color: '#94a3b8',
        size: 11,
      },
      margin: { l: 45, r: 20, t: 30, b: 40 },
      xaxis: {
        gridcolor: '#1e293b',
        zerolinecolor: '#334155',
        tickfont: { color: '#94a3b8', size: 10 },
        ...layout.xaxis,
      },
      yaxis: {
        gridcolor: '#1e293b',
        zerolinecolor: '#334155',
        tickfont: { color: '#94a3b8', size: 10 },
        ...layout.yaxis,
      },
      hoverlabel: {
        bgcolor: '#0f172a',
        bordercolor: '#334155',
        font: { family: 'Inter, sans-serif', size: 11, color: '#f8fafc' },
      },
      legend: {
        font: { color: '#cbd5e1', size: 10 },
        bgcolor: 'rgba(15, 23, 42, 0.6)',
        bordercolor: '#1e293b',
        borderwidth: 1,
        ...layout.legend,
      },
      autosize: true,
    };

    const mergedLayout: Partial<Plotly.Layout> = {
      ...darkDefaults,
      ...layout,
    };

    const defaultConfig: Partial<Plotly.Config> = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
      ...config,
    };

    Plotly.newPlot(containerRef.current, data, mergedLayout, defaultConfig);

    const handleResize = () => {
      if (containerRef.current) {
        Plotly.Plots.resize(containerRef.current);
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (containerRef.current) {
        Plotly.purge(containerRef.current);
      }
    };
  }, [data, layout, config]);

  return <div ref={containerRef} className={`w-full h-full min-h-[250px] ${className}`} style={style} />;
};
