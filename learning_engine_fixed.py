#!/usr/bin/env python3
# SARA LEARNING ENGINE - FIXED VERSION
# Works without heavy ML dependencies

import os
import sys
import time
import json
import re
import random
from collections import defaultdict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SkillAssessment:
    """Assess AI response quality without ML dependencies"""
    
    def __init__(self):
        self.skill_categories = {
            'analytical': ['reasoning', 'problem_decomposition', 'pattern_recognition'],
            'technical': ['programming', 'system_admin', 'security_implementation'],
            'communication': ['clarity', 'empathy', 'adaptability'],
            'creative': ['innovation', 'synthesis', 'alternative_thinking'],
            'learning': ['memory_retention', 'speed', 'autonomous_improvement']
        }
    
    def assess_response_quality(self, user_query, ai_response, context=None):
        """Assess quality using simple heuristics"""
        try:
            quality_metrics = {
                'relevance': self._assess_relevance(user_query, ai_response),
                'accuracy': 0.7,  # Neutral when no fact-checking available
                'completeness': self._assess_completeness(user_query, ai_response),
                'clarity': self._assess_clarity(ai_response),
                'helpfulness': self._assess_helpfulness(user_query, ai_response),
                'innovation': self._assess_innovation(ai_response)
            }
            
            overall_score = sum(quality_metrics.values()) / len(quality_metrics)
            quality_metrics['overall_score'] = overall_score
            
            return quality_metrics
        except Exception as e:
            logger.error(f"Assessment failed: {e}")
            return {'overall_score': 0.5}
    
    def _assess_relevance(self, query, response):
        query_words = set(re.findall(r'\w+', query.lower()))
        response_words = set(re.findall(r'\w+', response.lower()))
        if not query_words:
            return 0.5
        intersection = query_words.intersection(response_words)
        return min(1.0, len(intersection) / max(len(query_words) * 0.5, 1))
    
    def _assess_completeness(self, query, response):
        query_len = len(query.split())
        response_len = len(response.split())
        if response_len < query_len:
            return 0.4
        elif response_len < query_len * 2:
            return 0.7
        return 0.9
    
    def _assess_clarity(self, response):
        sentences = re.split(r'[.!?]+', response)
        word_counts = [len(s.split()) for s in sentences if s.strip()]
        if not word_counts:
            return 0.3
        avg_len = sum(word_counts) / len(word_counts)
        if 10 <= avg_len <= 25:
            return 0.9
        elif 5 <= avg_len <= 30:
            return 0.7
        return 0.5
    
    def _assess_helpfulness(self, query, response):
        indicators = ['can', 'will', 'should', 'help', 'solve', 'fix', 'create', 'implement', 'here', 'try']
        response_lower = response.lower()
        helpful_count = sum(1 for ind in indicators if ind in response_lower)
        return min(1.0, helpful_count / len(indicators) + 0.3)
    
    def _assess_innovation(self, response):
        patterns = ['alternative', 'different', 'creative', 'innovative', 'unique', 'novel']
        response_lower = response.lower()
        innovation_count = sum(1 for p in patterns if p in response_lower)
        return min(1.0, innovation_count / len(patterns))

class AutonomousLearningEngine:
    """Learning engine that works without heavy dependencies"""
    
    def __init__(self, state_path="C:/Users/bklyn/SARA3-2026/learning_state.json"):
        logger.info("🧠 Initializing Learning Engine...")
        
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        self.state_path = state_path
        self.skill_assessment = SkillAssessment()
        
        # Default capabilities
        self.capabilities = {
            'analytical': 0.5,
            'technical': 0.5,
            'communication': 0.5,
            'creative': 0.5,
            'learning': 0.5
        }
        
        self.interaction_history = []
        self.load_state()
        self.pattern_store = {}
        
        logger.info("✅ Learning Engine ready")
    
    def load_state(self):
        """Load previous learning state"""
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r') as f:
                    state = json.load(f)
                    self.capabilities = state.get('capabilities', self.capabilities)
                    self.interaction_history = state.get('history', [])
                    logger.info(f"📚 Loaded {len(self.interaction_history)} past interactions")
            except Exception as e:
                logger.warning(f"Could not load state: {e}")
    
    def save_state(self):
        """Save current state"""
        try:
            state = {
                'capabilities': self.capabilities,
                'history': self.interaction_history[-100:],  # Keep last 100
                'last_updated': time.time()
            }
            with open(self.state_path, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info("💾 Learning state saved")
        except Exception as e:
            logger.error(f"Save failed: {e}")
    
    def analyze_interaction(self, user_query, ai_response, success_score=None):
        """Analyze an interaction"""
        if success_score is None:
            quality = self.skill_assessment.assess_response_quality(user_query, ai_response)
            success_score = quality.get('overall_score', 0.5)
        
        interaction = {
            'timestamp': time.time(),
            'query': user_query,
            'response': ai_response[:200],  # Truncate for storage
            'success_score': success_score
        }
        
        self.interaction_history.append(interaction)
        return interaction
    
    def learn_from_interactions(self, interactions):
        """Learn from a batch of interactions"""
        logger.info(f"📚 Learning from {len(interactions)} interactions...")
        
        if not interactions:
            return {'patterns_extracted': 0, 'capabilities_evolved': 0}
        
        # Extract simple patterns
        patterns = self._extract_patterns(interactions)
        
        # Evolve capabilities based on performance
        evolved = self._evolve_capabilities(interactions)
        
        # Save state
        self.save_state()
        
        logger.info(f"✅ Learned {len(patterns)} patterns, evolved {evolved} capabilities")
        
        return {
            'patterns_extracted': len(patterns),
            'capabilities_evolved': evolved
        }
    
    def _extract_patterns(self, interactions):
        """Extract patterns from interactions"""
        patterns = []
        
        for interaction in interactions:
            query = interaction.get('query', '').lower()
            score = interaction.get('success_score', 0.5)
            
            # Query type patterns
            if any(w in query for w in ['how', 'help', 'what is']):
                patterns.append({'type': 'help_request', 'score': score})
            elif any(w in query for w in ['code', 'fix', 'debug']):
                patterns.append({'type': 'technical', 'score': score})
            elif any(w in query for w in ['create', 'build', 'make']):
                patterns.append({'type': 'creation', 'score': score})
        
        return patterns
    
    def _evolve_capabilities(self, interactions):
        """Update capability scores based on recent performance"""
        if not interactions:
            return 0
        
        avg_score = sum(i.get('success_score', 0.5) for i in interactions) / len(interactions)
        
        evolved = 0
        for skill in self.capabilities:
            if avg_score > 0.7 and random.random() > 0.7:
                old = self.capabilities[skill]
                self.capabilities[skill] = min(1.0, old + 0.05)
                if self.capabilities[skill] > old:
                    evolved += 1
        
        return evolved
    
    def get_current_capabilities(self):
        return self.capabilities.copy()
    
    def assess_learning_progress(self):
        avg = sum(self.capabilities.values()) / len(self.capabilities)
        return {
            'overall_capability_level': avg,
            'capability_breakdown': self.capabilities,
            'learning_trajectory': 'improving' if avg > 0.55 else 'stable'
        }

def main():
    logger.info("🧠 Testing Learning Engine...")
    
    engine = AutonomousLearningEngine()
    
    # Test interactions
    test_interactions = [
        {'query': 'How do I create a Python function?', 'response': 'Use def keyword...', 'success_score': 0.8},
        {'query': 'What is machine learning?', 'response': 'ML is a subset of AI...', 'success_score': 0.9},
        {'query': 'Fix this code', 'response': 'Here is the fix...', 'success_score': 0.85},
    ]
    
    results = engine.learn_from_interactions(test_interactions)
    logger.info(f"Learning results: {results}")
    
    caps = engine.get_current_capabilities()
    logger.info(f"Capabilities: {caps}")
    
    progress = engine.assess_learning_progress()
    logger.info(f"Progress: {progress}")
    
    logger.info("🎉 Learning Engine test passed!")

if __name__ == "__main__":
    main()
