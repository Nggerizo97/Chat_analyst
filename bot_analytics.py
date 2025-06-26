#!/usr/bin/env python3
"""
Bot Analytics Dashboard
======================

Analyzes chat bot conversation data to provide insights on:
- Bot usage metrics and costs
- Channel distribution analysis
- Advisor escalation patterns
- Cost analysis vs target metrics

This script processes conversation data from JSON files and Excel exports
to generate comprehensive analytics for client presentations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configure plot styling
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Cost Constants (from requirements)
COST_PER_INTERACTION = 75  # $75 per interaction
COST_PER_ADVISOR_STEP = 300  # $300 per advisor escalation
COST_PER_ADVISOR_HOUR = 23000  # $23,000 per advisor hour
TARGET_AVG_INTERACTIONS = 20  # Target average interactions per conversation
TARGET_ADVISOR_PERCENTAGE = 30  # Target percentage going to advisor (30%)
ADVISOR_TIME_MIN = 5  # Minimum advisor time in minutes
ADVISOR_TIME_MAX = 10  # Maximum advisor time in minutes

class BotAnalytics:
    """Main class for bot analytics and reporting."""
    
    def __init__(self, json_file='Conversación_2.json', excel_file='Excel_completo.xlsx'):
        """Initialize with data files."""
        self.json_file = json_file
        self.excel_file = excel_file
        self.raw_data = None
        self.processed_data = None
        self.excel_data = None
        
    def load_data(self):
        """Load and process data from JSON and Excel files."""
        print("Loading conversation data...")
        
        # Load JSON data
        conversations = []
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        if 'result' in record:
                            context = json.loads(record['result']['_raw'])['request']['context']
                            conversations.append(context)
            
            self.raw_data = pd.DataFrame(conversations)
            print(f"Loaded {len(conversations)} conversations from JSON")
        except Exception as e:
            print(f"Error loading JSON data: {e}")
            return False
            
        # Load Excel data
        try:
            self.excel_data = pd.read_excel(self.excel_file)
            print(f"Loaded Excel data with {len(self.excel_data)} records")
        except Exception as e:
            print(f"Error loading Excel data: {e}")
            
        return True
    
    def process_conversations(self):
        """Process conversation data to extract metrics."""
        if self.raw_data is None:
            print("No data loaded. Call load_data() first.")
            return
            
        processed = []
        
        for idx, row in self.raw_data.iterrows():
            try:
                # Basic conversation info
                conv_data = {
                    'conversation_id': row.get('conversation_id', f'conv_{idx}'),
                    'bot_session': row.get('bot_session', ''),
                    'fecha': row.get('fecha', ''),
                    'channel': self._extract_channel(row.get('channelId', '')),
                    'user_id': row.get('afiliadoid', ''),
                }
                
                # Process chat history
                chat_history = row.get('chatHistory', [])
                if isinstance(chat_history, list):
                    conv_data.update(self._analyze_chat_history(chat_history))
                else:
                    conv_data.update({
                        'total_messages': 0,
                        'user_messages': 0,
                        'bot_messages': 0,
                        'conversation_duration_minutes': 0,
                        'interactions_count': 0
                    })
                
                # Advisor escalation data
                conv_data['went_to_advisor'] = row.get('datosParaAsesor') is not None
                conv_data['escalation_reason'] = row.get('nodo_origen', '')
                
                # Satisfaction data
                conv_data['satisfaction_rating'] = row.get('retroalimentacion', None)
                conv_data['feedback_comment'] = row.get('retroalimentacion_comentario', '')
                
                # Add to processed list
                processed.append(conv_data)
                
            except Exception as e:
                print(f"Error processing conversation {idx}: {e}")
                continue
        
        self.processed_data = pd.DataFrame(processed)
        print(f"Processed {len(processed)} conversations successfully")
        
    def _extract_channel(self, channel_id):
        """Extract channel type from channelId."""
        if 'whatsapp' in str(channel_id).lower():
            return 'WhatsApp'
        elif 'directline' in str(channel_id).lower():
            return 'Web Portal'
        else:
            return 'Other'
    
    def _analyze_chat_history(self, chat_history):
        """Analyze chat history to extract metrics."""
        if not chat_history:
            return {
                'total_messages': 0,
                'user_messages': 0,
                'bot_messages': 0,
                'conversation_duration_minutes': 0,
                'interactions_count': 0
            }
        
        total_messages = len(chat_history)
        user_messages = sum(1 for msg in chat_history if not msg.get('from', {}).get('is_bot', True))
        bot_messages = total_messages - user_messages
        interactions = user_messages  # User interactions count
        
        # Calculate duration
        timestamps = [msg.get('datetime', 0) for msg in chat_history if msg.get('datetime')]
        duration_minutes = 0
        if len(timestamps) >= 2:
            duration_ms = max(timestamps) - min(timestamps)
            duration_minutes = duration_ms / (1000 * 60)  # Convert to minutes
        
        return {
            'total_messages': total_messages,
            'user_messages': user_messages,
            'bot_messages': bot_messages,
            'conversation_duration_minutes': duration_minutes,
            'interactions_count': interactions
        }
    
    def calculate_metrics(self):
        """Calculate key performance metrics."""
        if self.processed_data is None or len(self.processed_data) == 0:
            print("No processed data available")
            return {}
        
        df = self.processed_data
        
        # Basic metrics
        total_conversations = len(df)
        total_interactions = df['interactions_count'].sum()
        avg_interactions_per_conversation = df['interactions_count'].mean()
        
        # Advisor escalation metrics
        advisor_escalations = df['went_to_advisor'].sum()
        advisor_percentage = (advisor_escalations / total_conversations) * 100
        
        # Channel distribution
        channel_distribution = df['channel'].value_counts(normalize=True) * 100
        
        # Satisfaction metrics
        satisfaction_data = df['satisfaction_rating'].dropna()
        avg_satisfaction = satisfaction_data.mean() if len(satisfaction_data) > 0 else 0
        
        # Duration metrics
        avg_duration = df['conversation_duration_minutes'].mean()
        
        # Cost calculations
        interaction_costs = total_interactions * COST_PER_INTERACTION
        advisor_escalation_costs = advisor_escalations * COST_PER_ADVISOR_STEP
        
        # Estimate advisor time costs (assuming average 7.5 minutes per escalation)
        avg_advisor_time = (ADVISOR_TIME_MIN + ADVISOR_TIME_MAX) / 2
        advisor_time_hours = (advisor_escalations * avg_advisor_time) / 60
        advisor_time_costs = advisor_time_hours * COST_PER_ADVISOR_HOUR
        
        total_costs = interaction_costs + advisor_escalation_costs + advisor_time_costs
        
        metrics = {
            'total_conversations': total_conversations,
            'total_interactions': total_interactions,
            'avg_interactions_per_conversation': avg_interactions_per_conversation,
            'advisor_escalations': advisor_escalations,
            'advisor_percentage': advisor_percentage,
            'channel_distribution': channel_distribution.to_dict(),
            'avg_satisfaction': avg_satisfaction,
            'avg_duration_minutes': avg_duration,
            'costs': {
                'interaction_costs': interaction_costs,
                'advisor_escalation_costs': advisor_escalation_costs,
                'advisor_time_costs': advisor_time_costs,
                'total_costs': total_costs,
                'cost_per_conversation': total_costs / total_conversations if total_conversations > 0 else 0
            }
        }
        
        return metrics
    
    def create_visualizations(self, metrics):
        """Create comprehensive visualizations."""
        print("Creating visualizations...")
        
        # Set up the plotting style
        plt.rcParams['figure.figsize'] = (15, 10)
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Bot Analytics Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Channel Distribution
        if 'channel_distribution' in metrics and metrics['channel_distribution']:
            channels = list(metrics['channel_distribution'].keys())
            percentages = list(metrics['channel_distribution'].values())
            
            axes[0, 0].pie(percentages, labels=channels, autopct='%1.1f%%', startangle=90)
            axes[0, 0].set_title('Channel Distribution')
        
        # 2. Advisor Escalation Comparison
        target_vs_actual = [TARGET_ADVISOR_PERCENTAGE, metrics.get('advisor_percentage', 0)]
        labels = ['Target', 'Actual']
        
        bars = axes[0, 1].bar(labels, target_vs_actual, color=['lightblue', 'orange'])
        axes[0, 1].set_title('Advisor Escalation Rate (%)')
        axes[0, 1].set_ylabel('Percentage')
        
        # Add value labels on bars
        for bar, value in zip(bars, target_vs_actual):
            axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                           f'{value:.1f}%', ha='center', va='bottom')
        
        # 3. Interactions per Conversation
        target_vs_actual_interactions = [TARGET_AVG_INTERACTIONS, metrics.get('avg_interactions_per_conversation', 0)]
        
        bars = axes[0, 2].bar(labels, target_vs_actual_interactions, color=['lightgreen', 'red'])
        axes[0, 2].set_title('Average Interactions per Conversation')
        axes[0, 2].set_ylabel('Number of Interactions')
        
        for bar, value in zip(bars, target_vs_actual_interactions):
            axes[0, 2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                           f'{value:.1f}', ha='center', va='bottom')
        
        # 4. Cost Breakdown
        if 'costs' in metrics:
            costs = metrics['costs']
            cost_categories = ['Interactions', 'Advisor Steps', 'Advisor Time']
            cost_values = [
                costs['interaction_costs'],
                costs['advisor_escalation_costs'],
                costs['advisor_time_costs']
            ]
            
            bars = axes[1, 0].bar(cost_categories, cost_values, color=['skyblue', 'orange', 'green'])
            axes[1, 0].set_title('Cost Breakdown')
            axes[1, 0].set_ylabel('Cost ($)')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Format y-axis as currency
            axes[1, 0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # 5. Satisfaction Distribution (if available)
        if self.processed_data is not None and 'satisfaction_rating' in self.processed_data.columns:
            satisfaction_data = self.processed_data['satisfaction_rating'].dropna()
            if len(satisfaction_data) > 0:
                satisfaction_counts = satisfaction_data.value_counts().sort_index()
                axes[1, 1].bar(satisfaction_counts.index, satisfaction_counts.values)
                axes[1, 1].set_title('Customer Satisfaction Ratings')
                axes[1, 1].set_xlabel('Rating (1-5)')
                axes[1, 1].set_ylabel('Count')
        
        # 6. Key Metrics Summary (Text)
        axes[1, 2].axis('off')
        summary_text = f"""
        Key Metrics Summary:
        
        Total Conversations: {metrics.get('total_conversations', 0):,}
        Total Interactions: {metrics.get('total_interactions', 0):,}
        Avg Interactions/Conv: {metrics.get('avg_interactions_per_conversation', 0):.1f}
        
        Advisor Escalations: {metrics.get('advisor_escalations', 0):,}
        Escalation Rate: {metrics.get('advisor_percentage', 0):.1f}%
        
        Total Costs: ${metrics.get('costs', {}).get('total_costs', 0):,.2f}
        Cost per Conversation: ${metrics.get('costs', {}).get('cost_per_conversation', 0):.2f}
        
        Avg Satisfaction: {metrics.get('avg_satisfaction', 0):.1f}/5
        """
        
        axes[1, 2].text(0.1, 0.9, summary_text, transform=axes[1, 2].transAxes, 
                        fontsize=12, verticalalignment='top', fontfamily='monospace')
        
        plt.tight_layout()
        plt.savefig('bot_analytics_dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Dashboard saved as 'bot_analytics_dashboard.png'")
    
    def create_interactive_dashboard(self, metrics):
        """Create an interactive Plotly dashboard."""
        print("Creating interactive dashboard...")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=('Channel Distribution', 'Advisor Escalation Rate', 'Cost Breakdown',
                          'Interactions Distribution', 'Satisfaction Ratings', 'Key Metrics'),
            specs=[[{"type": "pie"}, {"type": "bar"}, {"type": "bar"}],
                   [{"type": "histogram"}, {"type": "bar"}, {"type": "table"}]]
        )
        
        # 1. Channel Distribution (Pie Chart)
        if 'channel_distribution' in metrics and metrics['channel_distribution']:
            fig.add_trace(
                go.Pie(
                    labels=list(metrics['channel_distribution'].keys()),
                    values=list(metrics['channel_distribution'].values()),
                    name="Channel Distribution"
                ),
                row=1, col=1
            )
        
        # 2. Advisor Escalation Rate
        fig.add_trace(
            go.Bar(
                x=['Target', 'Actual'],
                y=[TARGET_ADVISOR_PERCENTAGE, metrics.get('advisor_percentage', 0)],
                name="Escalation Rate",
                marker_color=['lightblue', 'orange']
            ),
            row=1, col=2
        )
        
        # 3. Cost Breakdown
        if 'costs' in metrics:
            costs = metrics['costs']
            fig.add_trace(
                go.Bar(
                    x=['Interactions', 'Advisor Steps', 'Advisor Time'],
                    y=[costs['interaction_costs'], costs['advisor_escalation_costs'], costs['advisor_time_costs']],
                    name="Costs",
                    marker_color=['skyblue', 'orange', 'green']
                ),
                row=1, col=3
            )
        
        # 4. Interactions Distribution
        if self.processed_data is not None:
            fig.add_trace(
                go.Histogram(
                    x=self.processed_data['interactions_count'],
                    name="Interactions",
                    nbinsx=20
                ),
                row=2, col=1
            )
        
        # 5. Satisfaction Ratings
        if self.processed_data is not None and 'satisfaction_rating' in self.processed_data.columns:
            satisfaction_data = self.processed_data['satisfaction_rating'].dropna()
            if len(satisfaction_data) > 0:
                satisfaction_counts = satisfaction_data.value_counts().sort_index()
                fig.add_trace(
                    go.Bar(
                        x=satisfaction_counts.index,
                        y=satisfaction_counts.values,
                        name="Satisfaction"
                    ),
                    row=2, col=2
                )
        
        # 6. Key Metrics Table
        metrics_table = [
            ['Metric', 'Value'],
            ['Total Conversations', f"{metrics.get('total_conversations', 0):,}"],
            ['Total Interactions', f"{metrics.get('total_interactions', 0):,}"],
            ['Avg Interactions/Conv', f"{metrics.get('avg_interactions_per_conversation', 0):.1f}"],
            ['Advisor Escalations', f"{metrics.get('advisor_escalations', 0):,}"],
            ['Escalation Rate', f"{metrics.get('advisor_percentage', 0):.1f}%"],
            ['Total Costs', f"${metrics.get('costs', {}).get('total_costs', 0):,.2f}"],
            ['Cost per Conversation', f"${metrics.get('costs', {}).get('cost_per_conversation', 0):.2f}"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=metrics_table[0], fill_color='lightblue'),
                cells=dict(values=list(zip(*metrics_table[1:])), fill_color='lightgray')
            ),
            row=2, col=3
        )
        
        # Update layout
        fig.update_layout(
            title_text="Interactive Bot Analytics Dashboard",
            showlegend=False,
            height=800
        )
        
        # Save as HTML
        fig.write_html("interactive_bot_dashboard.html")
        print("Interactive dashboard saved as 'interactive_bot_dashboard.html'")
        
        return fig
    
    def generate_report(self):
        """Generate a comprehensive text report."""
        metrics = self.calculate_metrics()
        
        print("\n" + "="*80)
        print("BOT ANALYTICS REPORT")
        print("="*80)
        
        print(f"\n📊 CONVERSATION OVERVIEW")
        print(f"   Total Conversations: {metrics.get('total_conversations', 0):,}")
        print(f"   Total User Interactions: {metrics.get('total_interactions', 0):,}")
        print(f"   Average Interactions per Conversation: {metrics.get('avg_interactions_per_conversation', 0):.1f}")
        print(f"   Target Interactions per Conversation: {TARGET_AVG_INTERACTIONS}")
        
        deviation = metrics.get('avg_interactions_per_conversation', 0) - TARGET_AVG_INTERACTIONS
        print(f"   Deviation from Target: {deviation:+.1f} interactions")
        
        print(f"\n🔄 ADVISOR ESCALATION ANALYSIS")
        print(f"   Conversations escalated to advisor: {metrics.get('advisor_escalations', 0):,}")
        print(f"   Actual escalation rate: {metrics.get('advisor_percentage', 0):.1f}%")
        print(f"   Target escalation rate: {TARGET_ADVISOR_PERCENTAGE}%")
        
        escalation_deviation = metrics.get('advisor_percentage', 0) - TARGET_ADVISOR_PERCENTAGE
        print(f"   Deviation from Target: {escalation_deviation:+.1f}%")
        
        print(f"\n📱 CHANNEL DISTRIBUTION")
        if 'channel_distribution' in metrics:
            for channel, percentage in metrics['channel_distribution'].items():
                print(f"   {channel}: {percentage:.1f}%")
        
        print(f"\n💰 COST ANALYSIS")
        if 'costs' in metrics:
            costs = metrics['costs']
            print(f"   Interaction Costs (${COST_PER_INTERACTION}/interaction): ${costs['interaction_costs']:,.2f}")
            print(f"   Advisor Step Costs (${COST_PER_ADVISOR_STEP}/escalation): ${costs['advisor_escalation_costs']:,.2f}")
            print(f"   Advisor Time Costs (${COST_PER_ADVISOR_HOUR}/hour): ${costs['advisor_time_costs']:,.2f}")
            print(f"   ─────────────────────────────────────")
            print(f"   TOTAL COSTS: ${costs['total_costs']:,.2f}")
            print(f"   Cost per Conversation: ${costs['cost_per_conversation']:,.2f}")
        
        print(f"\n⭐ CUSTOMER SATISFACTION")
        print(f"   Average Satisfaction Rating: {metrics.get('avg_satisfaction', 0):.1f}/5.0")
        
        print(f"\n⏱️  CONVERSATION DURATION")
        print(f"   Average Duration: {metrics.get('avg_duration_minutes', 0):.1f} minutes")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        if metrics.get('avg_interactions_per_conversation', 0) > TARGET_AVG_INTERACTIONS:
            print("   • Consider optimizing bot responses to reduce interaction count")
        if metrics.get('advisor_percentage', 0) > TARGET_ADVISOR_PERCENTAGE:
            print("   • High advisor escalation rate - review bot knowledge base")
        if metrics.get('avg_satisfaction', 0) < 4.0:
            print("   • Customer satisfaction could be improved")
        
        print("\n" + "="*80)
        
        return metrics
    
    def run_complete_analysis(self):
        """Run the complete analytics pipeline."""
        print("Starting Bot Analytics Analysis...")
        print("-" * 50)
        
        # Load and process data
        if not self.load_data():
            return
        
        self.process_conversations()
        
        # Calculate metrics
        metrics = self.calculate_metrics()
        
        # Generate report
        self.generate_report()
        
        # Create visualizations
        self.create_visualizations(metrics)
        
        # Create interactive dashboard
        self.create_interactive_dashboard(metrics)
        
        print("\nAnalysis complete! Check the generated files:")
        print("- bot_analytics_dashboard.png (Static dashboard)")
        print("- interactive_bot_dashboard.html (Interactive dashboard)")
        
        return metrics


def main():
    """Main function to run the analytics."""
    # Initialize analytics
    analytics = BotAnalytics()
    
    # Run complete analysis
    results = analytics.run_complete_analysis()
    
    return results


if __name__ == "__main__":
    main()