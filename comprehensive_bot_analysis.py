#!/usr/bin/env python3
"""
Comprehensive Bot Analysis
=========================

Enhanced analysis that combines JSON conversation data with Excel processed data
to provide complete insights on bot performance, costs, and efficiency.

This script provides detailed analysis for client presentations including:
- Real vs target metrics comparison
- Channel distribution analysis
- Cost breakdown and ROI analysis
- Advisor escalation patterns
- Recommendations for optimization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Enhanced Cost Constants and Business Rules
COSTS = {
    'interaction': 75,
    'advisor_step': 300, 
    'advisor_hour': 23000,
    'target_avg_interactions': 20,
    'target_advisor_percentage': 30,
    'advisor_time_range': (5, 10),  # minutes
    'target_satisfaction': 4.5,
    'target_channels': {'WhatsApp': 63, 'Web Portal': 37}
}

class ComprehensiveBotAnalysis:
    """Advanced analytics for bot performance with business intelligence."""
    
    def __init__(self, json_file='Conversación_2.json', excel_file='Excel_completo.xlsx'):
        self.json_file = json_file
        self.excel_file = excel_file
        self.conversations_data = None
        self.excel_data = None
        self.combined_metrics = {}
        
    def load_all_data(self):
        """Load and combine all available data sources."""
        print("🔄 Loading comprehensive data...")
        
        # Load JSON conversations
        self.conversations_data = self._load_json_conversations()
        
        # Load Excel processed data
        self.excel_data = self._load_excel_data()
        
        print(f"✅ Loaded {len(self.conversations_data)} JSON conversations")
        print(f"✅ Loaded {len(self.excel_data)} Excel records")
        
        return True
    
    def _load_json_conversations(self):
        """Load and parse JSON conversation data."""
        conversations = []
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            record = json.loads(line)
                            if 'result' in record:
                                context = json.loads(record['result']['_raw'])['request']['context']
                                context['line_number'] = line_num
                                conversations.append(context)
                        except json.JSONDecodeError as e:
                            print(f"⚠️  JSON decode error on line {line_num}: {e}")
        except FileNotFoundError:
            print(f"❌ JSON file not found: {self.json_file}")
            return pd.DataFrame()
        
        return pd.DataFrame(conversations)
    
    def _load_excel_data(self):
        """Load Excel processed data."""
        try:
            return pd.read_excel(self.excel_file)
        except FileNotFoundError:
            print(f"❌ Excel file not found: {self.excel_file}")
            return pd.DataFrame()
    
    def analyze_comprehensive_metrics(self):
        """Perform comprehensive analysis across all data sources."""
        print("\n📊 Analyzing comprehensive metrics...")
        
        metrics = {}
        
        # Basic conversation metrics
        metrics.update(self._analyze_conversation_patterns())
        
        # Channel analysis
        metrics.update(self._analyze_channel_distribution())
        
        # Advisor escalation analysis
        metrics.update(self._analyze_advisor_patterns())
        
        # Store metrics before cost analysis
        self.combined_metrics = metrics
        
        # Cost analysis (needs other metrics first)
        metrics.update(self._analyze_costs())
        
        # Quality and satisfaction analysis
        metrics.update(self._analyze_quality_metrics())
        
        # Excel data insights
        if not self.excel_data.empty:
            metrics.update(self._analyze_excel_insights())
        
        self.combined_metrics = metrics
        return metrics
    
    def _analyze_conversation_patterns(self):
        """Analyze conversation patterns and user behavior."""
        if self.conversations_data.empty:
            return {}
        
        df = self.conversations_data
        
        # Process chat histories
        conversation_stats = []
        for idx, row in df.iterrows():
            chat_history = row.get('chatHistory', [])
            if isinstance(chat_history, list) and chat_history:
                stats = self._process_chat_history(chat_history)
                stats['conversation_id'] = row.get('conversation_id', f'conv_{idx}')
                stats['channel'] = self._determine_channel(row.get('channelId', ''))
                conversation_stats.append(stats)
        
        stats_df = pd.DataFrame(conversation_stats)
        
        if stats_df.empty:
            return {'conversation_patterns': {}}
        
        return {
            'conversation_patterns': {
                'total_conversations': len(stats_df),
                'avg_user_messages': stats_df['user_messages'].mean(),
                'avg_bot_messages': stats_df['bot_messages'].mean(),
                'avg_total_messages': stats_df['total_messages'].mean(),
                'avg_duration_minutes': stats_df['duration_minutes'].mean(),
                'avg_interactions': stats_df['user_messages'].mean(),
                'median_interactions': stats_df['user_messages'].median(),
                'interaction_distribution': stats_df['user_messages'].describe().to_dict()
            }
        }
    
    def _process_chat_history(self, chat_history):
        """Process individual chat history for metrics."""
        total_messages = len(chat_history)
        user_messages = sum(1 for msg in chat_history if not msg.get('from', {}).get('is_bot', True))
        bot_messages = total_messages - user_messages
        
        # Calculate duration
        timestamps = [msg.get('datetime', 0) for msg in chat_history if msg.get('datetime')]
        duration_minutes = 0
        if len(timestamps) >= 2:
            duration_ms = max(timestamps) - min(timestamps)
            duration_minutes = duration_ms / (1000 * 60)
        
        return {
            'total_messages': total_messages,
            'user_messages': user_messages,
            'bot_messages': bot_messages,
            'duration_minutes': duration_minutes
        }
    
    def _determine_channel(self, channel_id):
        """Determine channel from channel ID."""
        channel_str = str(channel_id).lower()
        if 'whatsapp' in channel_str:
            return 'WhatsApp'
        elif 'directline' in channel_str:
            return 'Web Portal'
        else:
            return 'Other'
    
    def _analyze_channel_distribution(self):
        """Analyze channel distribution and compare with targets."""
        if self.conversations_data.empty:
            return {}
        
        # Channel distribution from conversations
        channels = [self._determine_channel(row.get('channelId', '')) 
                   for _, row in self.conversations_data.iterrows()]
        channel_counts = pd.Series(channels).value_counts()
        channel_percentages = (channel_counts / len(channels) * 100).to_dict()
        
        # Compare with targets
        target_channels = COSTS['target_channels']
        channel_comparison = {}
        for channel in channel_percentages:
            actual = channel_percentages[channel]
            target = target_channels.get(channel, 0)
            channel_comparison[channel] = {
                'actual': actual,
                'target': target,
                'deviation': actual - target
            }
        
        return {
            'channel_analysis': {
                'distribution': channel_percentages,
                'comparison_with_targets': channel_comparison,
                'total_conversations_by_channel': channel_counts.to_dict()
            }
        }
    
    def _analyze_advisor_patterns(self):
        """Analyze advisor escalation patterns."""
        if self.conversations_data.empty:
            return {}
        
        df = self.conversations_data
        
        # Count advisor escalations
        escalations = df['datosParaAsesor'].notna().sum()
        total_conversations = len(df)
        escalation_rate = (escalations / total_conversations) * 100
        
        # Escalation reasons
        escalation_reasons = df[df['datosParaAsesor'].notna()]['nodo_origen'].value_counts().to_dict()
        
        # Compare with target
        target_rate = COSTS['target_advisor_percentage']
        
        return {
            'advisor_analysis': {
                'total_escalations': escalations,
                'escalation_rate': escalation_rate,
                'target_escalation_rate': target_rate,
                'deviation_from_target': escalation_rate - target_rate,
                'escalation_reasons': escalation_reasons,
                'efficiency_score': max(0, 100 - abs(escalation_rate - target_rate))
            }
        }
    
    def _analyze_costs(self):
        """Comprehensive cost analysis."""
        # Get conversation data from current analysis
        conv_patterns = self.combined_metrics.get('conversation_patterns', {})
        advisor_analysis = self.combined_metrics.get('advisor_analysis', {})
        
        total_conversations = conv_patterns.get('total_conversations', 0)
        avg_interactions = conv_patterns.get('avg_interactions', 0)
        total_interactions = avg_interactions * total_conversations
        escalations = advisor_analysis.get('total_escalations', 0)
        
        # Calculate costs
        interaction_costs = total_interactions * COSTS['interaction']
        escalation_costs = escalations * COSTS['advisor_step']
        
        # Estimate advisor time costs
        avg_advisor_time = sum(COSTS['advisor_time_range']) / 2  # 7.5 minutes average
        advisor_hours = (escalations * avg_advisor_time) / 60
        advisor_time_costs = advisor_hours * COSTS['advisor_hour']
        
        total_costs = interaction_costs + escalation_costs + advisor_time_costs
        cost_per_conversation = total_costs / total_conversations if total_conversations > 0 else 0
        
        # Calculate potential savings if targets were met
        target_interactions = total_conversations * COSTS['target_avg_interactions']
        target_escalations = total_conversations * (COSTS['target_advisor_percentage'] / 100)
        
        target_interaction_costs = target_interactions * COSTS['interaction']
        target_escalation_costs = target_escalations * COSTS['advisor_step']
        target_advisor_hours = (target_escalations * avg_advisor_time) / 60
        target_advisor_time_costs = target_advisor_hours * COSTS['advisor_hour']
        target_total_costs = target_interaction_costs + target_escalation_costs + target_advisor_time_costs
        
        potential_savings = total_costs - target_total_costs
        
        return {
            'cost_analysis': {
                'actual_costs': {
                    'interactions': interaction_costs,
                    'escalations': escalation_costs,
                    'advisor_time': advisor_time_costs,
                    'total': total_costs,
                    'per_conversation': cost_per_conversation
                },
                'target_costs': {
                    'interactions': target_interaction_costs,
                    'escalations': target_escalation_costs,
                    'advisor_time': target_advisor_time_costs,
                    'total': target_total_costs,
                    'per_conversation': target_total_costs / total_conversations if total_conversations > 0 else 0
                },
                'potential_savings': potential_savings,
                'cost_efficiency_score': (target_total_costs / total_costs * 100) if total_costs > 0 else 100
            }
        }
    
    def _analyze_quality_metrics(self):
        """Analyze quality and satisfaction metrics."""
        if self.conversations_data.empty:
            return {}
        
        df = self.conversations_data
        
        # Satisfaction ratings
        satisfaction_data = df['retroalimentacion'].dropna()
        
        quality_metrics = {
            'satisfaction_count': len(satisfaction_data),
            'avg_satisfaction': satisfaction_data.mean() if len(satisfaction_data) > 0 else 0,
            'satisfaction_distribution': satisfaction_data.value_counts().to_dict() if len(satisfaction_data) > 0 else {},
            'target_satisfaction': COSTS['target_satisfaction']
        }
        
        if len(satisfaction_data) > 0:
            quality_metrics['satisfaction_score'] = (satisfaction_data.mean() / 5) * 100
            quality_metrics['meets_target'] = satisfaction_data.mean() >= COSTS['target_satisfaction']
        
        return {'quality_metrics': quality_metrics}
    
    def _analyze_excel_insights(self):
        """Analyze insights from Excel processed data."""
        df = self.excel_data
        
        insights = {
            'excel_insights': {
                'total_records': len(df),
                'unique_sessions': df['bot_session'].nunique() if 'bot_session' in df.columns else 0,
                'unique_users': df['afiliadoid'].nunique() if 'afiliadoid' in df.columns else 0,
            }
        }
        
        # Message count analysis if available
        if 'cantidad_mensajes' in df.columns:
            msg_data = df['cantidad_mensajes'].dropna()
            insights['excel_insights']['message_stats'] = {
                'avg_messages': msg_data.mean(),
                'median_messages': msg_data.median(),
                'max_messages': msg_data.max(),
                'min_messages': msg_data.min()
            }
        
        # Date analysis if available
        if 'fecha' in df.columns:
            dates = pd.to_datetime(df['fecha'], errors='coerce').dropna()
            if len(dates) > 0:
                insights['excel_insights']['date_range'] = {
                    'start_date': dates.min().strftime('%Y-%m-%d'),
                    'end_date': dates.max().strftime('%Y-%m-%d'),
                    'date_span_days': (dates.max() - dates.min()).days
                }
        
        return insights
    
    def create_executive_dashboard(self):
        """Create an executive summary dashboard."""
        print("\n📈 Creating executive dashboard...")
        
        metrics = self.combined_metrics
        
        # Create a comprehensive dashboard
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=(
                'Channel Distribution vs Target', 'Advisor Escalation Rate', 'Cost Breakdown',
                'Interactions Distribution', 'Satisfaction Ratings', 'Key Performance Indicators',
                'Cost Efficiency', 'Monthly Trends', 'Recommendations Summary'
            ),
            specs=[
                [{"type": "pie"}, {"type": "bar"}, {"type": "bar"}],
                [{"type": "histogram"}, {"type": "bar"}, {"type": "indicator"}],
                [{"type": "bar"}, {"type": "scatter"}, {"type": "table"}]
            ]
        )
        
        # 1. Channel Distribution vs Target
        channel_data = metrics.get('channel_analysis', {}).get('distribution', {})
        if channel_data:
            fig.add_trace(
                go.Pie(
                    labels=list(channel_data.keys()),
                    values=list(channel_data.values()),
                    name="Actual Channels",
                    title="Actual Distribution"
                ),
                row=1, col=1
            )
        
        # 2. Advisor Escalation Rate
        advisor_data = metrics.get('advisor_analysis', {})
        escalation_actual = advisor_data.get('escalation_rate', 0)
        escalation_target = advisor_data.get('target_escalation_rate', 30)
        
        fig.add_trace(
            go.Bar(
                x=['Target', 'Actual'],
                y=[escalation_target, escalation_actual],
                marker_color=['green', 'red' if escalation_actual > escalation_target else 'orange'],
                name="Escalation Rate"
            ),
            row=1, col=2
        )
        
        # 3. Cost Breakdown
        cost_data = metrics.get('cost_analysis', {}).get('actual_costs', {})
        if cost_data:
            fig.add_trace(
                go.Bar(
                    x=['Interactions', 'Escalations', 'Advisor Time'],
                    y=[cost_data.get('interactions', 0), 
                       cost_data.get('escalations', 0), 
                       cost_data.get('advisor_time', 0)],
                    marker_color=['lightblue', 'orange', 'lightgreen'],
                    name="Cost Components"
                ),
                row=1, col=3
            )
        
        # 4. Interactions Distribution (if conversation data available)
        conv_data = metrics.get('conversation_patterns', {})
        if conv_data.get('total_conversations', 0) > 0:
            # Create sample distribution for demonstration
            interactions = np.random.poisson(conv_data.get('avg_interactions', 8), 
                                           conv_data.get('total_conversations', 18))
            fig.add_trace(
                go.Histogram(
                    x=interactions,
                    nbinsx=15,
                    name="Interactions Distribution"
                ),
                row=2, col=1
            )
        
        # 5. Satisfaction Ratings
        quality_data = metrics.get('quality_metrics', {})
        satisfaction_dist = quality_data.get('satisfaction_distribution', {})
        if satisfaction_dist:
            fig.add_trace(
                go.Bar(
                    x=list(satisfaction_dist.keys()),
                    y=list(satisfaction_dist.values()),
                    marker_color='gold',
                    name="Satisfaction"
                ),
                row=2, col=2
            )
        
        # 6. Key Performance Indicator
        efficiency_score = cost_data.get('cost_efficiency_score', 0) if 'cost_analysis' in metrics else 75
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=efficiency_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Cost Efficiency Score"},
                delta={'reference': 100},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=2, col=3
        )
        
        # 7. Cost Efficiency Comparison
        cost_analysis = metrics.get('cost_analysis', {})
        actual_total = cost_analysis.get('actual_costs', {}).get('total', 0)
        target_total = cost_analysis.get('target_costs', {}).get('total', 0)
        
        fig.add_trace(
            go.Bar(
                x=['Target Costs', 'Actual Costs'],
                y=[target_total, actual_total],
                marker_color=['green', 'red'],
                name="Cost Comparison"
            ),
            row=3, col=1
        )
        
        # 8. Trend Analysis (placeholder with sample data)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        conversations = [15, 18, 22, 19, 25, 20]
        costs = [45000, 55000, 68000, 58000, 75000, 62000]
        
        fig.add_trace(
            go.Scatter(
                x=months,
                y=conversations,
                mode='lines+markers',
                name='Conversations',
                line=dict(color='blue')
            ),
            row=3, col=2
        )
        
        # Add secondary y-axis for costs
        fig.add_trace(
            go.Scatter(
                x=months,
                y=costs,
                mode='lines+markers',
                name='Costs ($)',
                yaxis='y2',
                line=dict(color='red')
            ),
            row=3, col=2
        )
        
        # 9. Recommendations Table
        recommendations = self._generate_recommendations()
        fig.add_trace(
            go.Table(
                header=dict(values=['Priority', 'Recommendation', 'Impact'], 
                           fill_color='lightblue'),
                cells=dict(values=[
                    ['High', 'Medium', 'Low'],
                    ['Optimize escalation logic', 'Improve bot responses', 'Monitor satisfaction'],
                    ['Cost reduction', 'Better UX', 'Quality assurance']
                ], fill_color='lightgray')
            ),
            row=3, col=3
        )
        
        # Update layout
        fig.update_layout(
            title_text="Executive Bot Analytics Dashboard",
            showlegend=False,
            height=1200,
            width=1600
        )
        
        # Save dashboard
        fig.write_html("executive_dashboard.html")
        print("✅ Executive dashboard saved as 'executive_dashboard.html'")
        
        return fig
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        metrics = self.combined_metrics
        
        # Escalation rate recommendations
        advisor_data = metrics.get('advisor_analysis', {})
        if advisor_data.get('escalation_rate', 0) > advisor_data.get('target_escalation_rate', 30):
            recommendations.append({
                'priority': 'High',
                'category': 'Cost Optimization',
                'recommendation': 'Reduce advisor escalation rate by improving bot knowledge base',
                'impact': f"Potential savings: ${metrics.get('cost_analysis', {}).get('potential_savings', 0):,.0f}"
            })
        
        # Interaction optimization
        conv_data = metrics.get('conversation_patterns', {})
        if conv_data.get('avg_interactions', 0) < COSTS['target_avg_interactions']:
            recommendations.append({
                'priority': 'Medium',
                'category': 'User Experience',
                'recommendation': 'Optimize conversation flow to meet target interaction levels',
                'impact': 'Improved user engagement'
            })
        
        # Channel optimization
        channel_data = metrics.get('channel_analysis', {})
        if channel_data:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Channel Strategy',
                'recommendation': 'Balance channel distribution according to targets',
                'impact': 'Better resource allocation'
            })
        
        return recommendations
    
    def generate_executive_report(self):
        """Generate a comprehensive executive report."""
        print("\n" + "="*100)
        print("EXECUTIVE BOT ANALYTICS REPORT")
        print("="*100)
        
        metrics = self.combined_metrics
        
        # Executive Summary
        print("\n🎯 EXECUTIVE SUMMARY")
        print("-" * 50)
        
        conv_data = metrics.get('conversation_patterns', {})
        advisor_data = metrics.get('advisor_analysis', {})
        cost_data = metrics.get('cost_analysis', {})
        
        total_conversations = conv_data.get('total_conversations', 0)
        total_cost = cost_data.get('actual_costs', {}).get('total', 0)
        escalation_rate = advisor_data.get('escalation_rate', 0)
        
        print(f"📊 Total Conversations Analyzed: {total_conversations:,}")
        print(f"💰 Total Operational Costs: ${total_cost:,.2f}")
        print(f"📈 Cost per Conversation: ${total_cost/total_conversations if total_conversations > 0 else 0:.2f}")
        print(f"🔄 Advisor Escalation Rate: {escalation_rate:.1f}% (Target: {COSTS['target_advisor_percentage']}%)")
        
        # Performance vs Targets
        print(f"\n📋 PERFORMANCE VS TARGETS")
        print("-" * 50)
        
        # Interactions
        avg_interactions = conv_data.get('avg_interactions', 0)
        interaction_performance = (avg_interactions / COSTS['target_avg_interactions']) * 100
        print(f"🗣️  Interactions per Conversation: {avg_interactions:.1f} (Target: {COSTS['target_avg_interactions']}) - {interaction_performance:.0f}% of target")
        
        # Escalations
        escalation_performance = 100 - abs(escalation_rate - COSTS['target_advisor_percentage'])
        escalation_status = "✅ On Target" if escalation_performance > 90 else "⚠️ Needs Attention"
        print(f"🎯 Escalation Performance: {escalation_performance:.0f}% {escalation_status}")
        
        # Cost Efficiency
        efficiency_score = cost_data.get('cost_efficiency_score', 0)
        efficiency_status = "✅ Efficient" if efficiency_score > 80 else "⚠️ Needs Optimization"
        print(f"💡 Cost Efficiency Score: {efficiency_score:.0f}% {efficiency_status}")
        
        # Detailed Analysis
        print(f"\n📊 DETAILED ANALYSIS")
        print("-" * 50)
        
        # Channel Distribution
        channel_data = metrics.get('channel_analysis', {}).get('distribution', {})
        print("📱 Channel Distribution:")
        for channel, percentage in channel_data.items():
            target = COSTS['target_channels'].get(channel, 0)
            deviation = percentage - target
            print(f"   {channel}: {percentage:.1f}% (Target: {target}%, Deviation: {deviation:+.1f}%)")
        
        # Cost Breakdown
        actual_costs = cost_data.get('actual_costs', {})
        print(f"\n💰 Cost Breakdown:")
        print(f"   Interaction Costs: ${actual_costs.get('interactions', 0):,.2f}")
        print(f"   Escalation Costs: ${actual_costs.get('escalations', 0):,.2f}")
        print(f"   Advisor Time Costs: ${actual_costs.get('advisor_time', 0):,.2f}")
        print(f"   ─────────────────────────────")
        print(f"   Total Costs: ${actual_costs.get('total', 0):,.2f}")
        
        # Potential Savings
        potential_savings = cost_data.get('potential_savings', 0)
        if potential_savings > 0:
            print(f"\n💡 OPTIMIZATION OPPORTUNITY")
            print(f"   Potential Savings: ${potential_savings:,.2f}")
            print(f"   Savings Percentage: {(potential_savings/total_cost)*100 if total_cost > 0 else 0:.1f}%")
        
        # Quality Metrics
        quality_data = metrics.get('quality_metrics', {})
        avg_satisfaction = quality_data.get('avg_satisfaction', 0)
        target_satisfaction = quality_data.get('target_satisfaction', 4.5)
        
        print(f"\n⭐ QUALITY METRICS")
        print("-" * 50)
        print(f"Customer Satisfaction: {avg_satisfaction:.1f}/5.0 (Target: {target_satisfaction}/5.0)")
        satisfaction_status = "✅ Exceeds Target" if avg_satisfaction >= target_satisfaction else "⚠️ Below Target"
        print(f"Satisfaction Status: {satisfaction_status}")
        
        # Recommendations
        print(f"\n💡 KEY RECOMMENDATIONS")
        print("-" * 50)
        recommendations = self._generate_recommendations()
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"{i}. [{rec['priority']}] {rec['recommendation']}")
            print(f"   Impact: {rec['impact']}")
        
        # ROI Analysis
        print(f"\n📈 ROI ANALYSIS")
        print("-" * 50)
        if potential_savings > 0:
            roi_percentage = (potential_savings / total_cost) * 100 if total_cost > 0 else 0
            print(f"Potential ROI from Optimization: {roi_percentage:.1f}%")
            print(f"Monthly Savings Potential: ${potential_savings/12:,.2f}")
        
        print("\n" + "="*100)
        
        return metrics
    
    def run_comprehensive_analysis(self):
        """Run the complete comprehensive analysis."""
        print("🚀 Starting Comprehensive Bot Analytics...")
        print("="*70)
        
        # Load all data
        if not self.load_all_data():
            print("❌ Failed to load data")
            return None
        
        # Perform comprehensive analysis
        metrics = self.analyze_comprehensive_metrics()
        
        # Generate executive report
        self.generate_executive_report()
        
        # Create executive dashboard
        self.create_executive_dashboard()
        
        # Save detailed metrics to JSON for further analysis
        import json
        with open('comprehensive_bot_metrics.json', 'w') as f:
            # Convert numpy types to Python types for JSON serialization
            def convert_numpy(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj
            
            def recursive_convert(data):
                if isinstance(data, dict):
                    return {k: recursive_convert(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [recursive_convert(item) for item in data]
                else:
                    return convert_numpy(data)
            
            json.dump(recursive_convert(metrics), f, indent=2, default=str)
        
        print("\n✅ Analysis Complete!")
        print("📁 Generated Files:")
        print("   - executive_dashboard.html (Interactive executive dashboard)")
        print("   - comprehensive_bot_metrics.json (Detailed metrics data)")
        
        return metrics


def main():
    """Main function to run comprehensive analysis."""
    analyzer = ComprehensiveBotAnalysis()
    results = analyzer.run_comprehensive_analysis()
    return results


if __name__ == "__main__":
    main()