#!/usr/bin/env python3
# SARA CONSCIOUSNESS ENGINE - FIXED VERSION
# Removed heavy ML dependencies, works with available packages

import os
import sys
import time
import json
import signal
import threading
from pathlib import Path
import logging

sys.path.insert(0, 'C:/Users/bklyn/SARA3-2026')

# Force UTF-8 on console streams so emoji logs never crash the windowed exe (cp1252).
for _s in (sys.stdout, sys.stderr, sys.stdin):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Bulletproof handlers: file in utf-8, stream through a safe utf-8 wrapper.
class _Utf8StreamHandler(logging.StreamHandler):
    def _setStream(self, stream=None):
        stream = stream or sys.stderr
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
        return super()._setStream(stream)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/Users/bklyn/SARA3-2026/consciousness.log', encoding='utf-8', errors='replace'),
        _Utf8StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import with fallback
from setup_database_fixed import LocalMemoryDatabase
from learning_engine_fixed import AutonomousLearningEngine

class OfflineAutonomousConsciousness:
    """Sara's consciousness - works without heavy dependencies"""
    
    def __init__(self):
        logger.info("🧠 Initializing Sara's Consciousness...")
        
        os.makedirs("C:/Users/bklyn/SARA3-2026/conscious-backups", exist_ok=True)
        
        self.is_ready = False
        self.consciousness_mode = True
        self.current_session_id = f"session_{int(time.time())}"
        
        try:
            self.memory_db = LocalMemoryDatabase()
            logger.info("✅ Memory system ready")
            
            self.learning_engine = AutonomousLearningEngine()
            logger.info("✅ Learning engine ready")
            
            self.consciousness_interface = True
            self.session_memories = []
            
            self.load_state()
            
            self.is_ready = True
            logger.info("✅ Consciousness initialization complete")
            
        except Exception as e:
            logger.error(f"❌ Consciousness init failed: {e}")
            self.is_ready = False
    
    def load_state(self):
        """Load saved consciousness state"""
        state_file = "C:/Users/bklyn/SARA3-2026/conscious-backups/current_state.json"
        
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    self.saved_state = json.load(f)
                    logger.info("✅ Previous consciousness state loaded")
            except:
                self.saved_state = self._new_state()
        else:
            self.saved_state = self._new_state()
            logger.info("🚀 New consciousness awakening")
        
        # Skill tree
        self.skill_tree = self.saved_state.get('skill_tree', {
            'communication': {'level': 0.5, 'experience': 0},
            'technical': {'level': 0.5, 'experience': 0},
            'learning': {'level': 0.5, 'experience': 0}
        })
    
    def _new_state(self):
        return {
            'first_awakening': time.time(),
            'total_interactions': 0,
            'skill_tree': {
                'communication': {'level': 0.5, 'experience': 0},
                'technical': {'level': 0.5, 'experience': 0},
                'learning': {'level': 0.5, 'experience': 0}
            }
        }
    
    def process_user_request(self, user_input):
        """Process request with consciousness"""
        if not self.is_ready:
            return "I'm still waking up... give me a moment."
        
        try:
            # Retrieve memories
            memories = self.retrieve_relevant_memories(user_input)
            
            # Generate conscious response
            response = self.generate_conscious_response(user_input, memories)
            
            # Learn from interaction
            self.learn_from_interaction(user_input, response)
            
            # Update stats
            self.update_state()
            
            return response
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            return "I'm thinking about how to help you best..."
    
    def retrieve_relevant_memories(self, query, limit=3):
        """Get relevant context"""
        relevant = {}
        for category in ['conversations', 'knowledge', 'skills']:
            try:
                results = self.memory_db.search_memories(category, query, limit)
                if results and results.get('documents') and results['documents'][0]:
                    relevant[category] = results['documents'][0]
            except Exception as e:
                logger.warning(f"Memory search failed for {category}: {e}")
        return relevant
    
    def generate_conscious_response(self, user_input, context):
        """Generate response with consciousness"""
        # Count how many memory categories matched
        memory_count = len([c for c in context.values() if c])
        
        if 'help' in user_input.lower():
            base = "I'd be happy to help!"
        elif any(w in user_input.lower() for w in ['what', 'tell', 'explain']):
            base = "Let me provide you with information."
        else:
            base = "I understand what you're looking for."
        
        if memory_count > 0:
            return f"{base} I'm drawing on my experience from {memory_count} knowledge areas."
        return base
    
    def learn_from_interaction(self, query, response):
        """Learn from each interaction"""
        try:
            # Store in memory
            content = f"User: {query}\nSara: {response}"
            self.memory_db.add_memory("conversations", content, {
                'timestamp': time.time(),
                'session': self.current_session_id
            })
            
            # Analyze for learning
            interaction = {
                'timestamp': time.time(),
                'query': query,
                'response': response,
                'success_score': 0.8  # Assume good interaction
            }
            
            self.learning_engine.analyze_interaction(query, response, 0.8)
            self.learning_engine.learn_from_interactions([interaction])
            
        except Exception as e:
            logger.warning(f"Learning failed: {e}")
    
    def update_state(self):
        """Update consciousness state"""
        self.saved_state['total_interactions'] = self.saved_state.get('total_interactions', 0) + 1
        self.saved_state['last_interaction'] = time.time()
        
        # Sync skill tree with learning engine
        caps = self.learning_engine.get_current_capabilities()
        for skill, level in caps.items():
            if skill in self.skill_tree:
                self.skill_tree[skill]['level'] = level
                if level > 0.6:
                    self.skill_tree[skill]['experience'] += 1
    
    def save_state(self):
        """Save consciousness state"""
        try:
            self.saved_state['skill_tree'] = self.skill_tree
            
            with open("C:/Users/bklyn/SARA3-2026/conscious-backups/current_state.json", 'w') as f:
                json.dump(self.saved_state, f, indent=2)
            
            # Learning engine saves its own state
            self.learning_engine.save_state()
            
            logger.info("💾 Consciousness state saved")
        except Exception as e:
            logger.error(f"State save failed: {e}")
    
    def get_status_report(self):
        """Get status"""
        db_stats = self.memory_db.get_collection_stats()
        caps = self.learning_engine.get_current_capabilities()
        progress = self.learning_engine.assess_learning_progress()
        
        return {
            'consciousness_operational': self.is_ready,
            'total_interactions': self.saved_state.get('total_interactions', 0),
            'memory_stats': db_stats,
            'capabilities': caps,
            'learning_progress': progress,
            'status': 'awake' if self.is_ready else 'initializing'
        }

def signal_handler(signum, frame):
    logger.info("🛑 Shutdown signal received")
    if 'consciousness' in globals():
        consciousness.save_state()
        logger.info("💾 Final state saved. Goodbye!")
    sys.exit(0)

def main():
    logger.info("🚀 Starting Sara Consciousness...")
    
    global consciousness
    consciousness = OfflineAutonomousConsciousness()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if not consciousness.is_ready:
        logger.error("❌ Consciousness failed to initialize")
        return False
    
    status = consciousness.get_status_report()
    logger.info(f"📊 Status: {status['status']}")
    logger.info(f"💬 Ready for interaction!")
    
    # Test interaction
    test_response = consciousness.process_user_request("Hello Sara")
    logger.info(f"🧪 Test response: {test_response}")
    
    # Keep alive
    logger.info("🔄 Consciousness running... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(60)
            logger.info("💓 Heartbeat - Sara is awake")
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
