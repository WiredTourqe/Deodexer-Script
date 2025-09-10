"""
Machine Learning optimization module for deodexing operations
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import pickle
import os
from pathlib import Path

from ..core.logger import logger
from ..core.config import config


class DeodexingOptimizer:
    """Machine learning-based optimization for deodexing parameters"""
    
    def __init__(self):
        self.model_path = config.get('ml.model_path', 'data/models/')
        self.enabled = config.get('ml.enabled', True)
        self.prediction_threshold = config.get('ml.prediction_threshold', 0.8)
        self.optimization_history = []
        
        # Feature weights for optimization
        self.feature_weights = {
            'file_size': 0.3,
            'complexity': 0.2,
            'api_level': 0.15,
            'file_type': 0.1,
            'system_load': 0.15,
            'historical_performance': 0.1
        }
        
        if self.enabled:
            self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize or load machine learning model"""
        try:
            # Create model directory if it doesn't exist
            os.makedirs(self.model_path, exist_ok=True)
            
            # For now, use a simple rule-based system
            # In a full implementation, this would load a trained ML model
            self.model_initialized = True
            logger.info("ML optimizer initialized", enabled=self.enabled)
            
        except Exception as e:
            logger.error("Failed to initialize ML model", error=str(e))
            self.enabled = False
    
    def optimize_parameters(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize deodexing parameters based on file characteristics"""
        if not self.enabled:
            return self._get_default_parameters()
        
        try:
            # Extract features for optimization
            features = self._extract_features(file_info)
            
            # Predict optimal parameters
            optimized_params = self._predict_optimal_parameters(features)
            
            # Validate and apply safety constraints
            optimized_params = self._apply_safety_constraints(optimized_params)
            
            logger.debug("Parameters optimized", 
                        file=file_info.get('name', 'unknown'),
                        optimized=optimized_params)
            
            return optimized_params
            
        except Exception as e:
            logger.error("Parameter optimization failed", error=str(e))
            return self._get_default_parameters()
    
    def _extract_features(self, file_info: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical features from file information"""
        features = {}
        
        # File size feature (normalized)
        file_size_mb = file_info.get('size_mb', 0)
        features['file_size_norm'] = min(file_size_mb / 100.0, 1.0)  # Normalize to 0-1
        
        # Complexity feature
        complexity_map = {'low': 0.2, 'medium': 0.5, 'high': 0.8}
        features['complexity'] = complexity_map.get(file_info.get('complexity', 'medium'), 0.5)
        
        # Estimated processing time (normalized)
        est_time = file_info.get('estimated_time', 30.0)
        features['est_time_norm'] = min(est_time / 300.0, 1.0)  # Normalize to 0-1 (max 5 min)
        
        # System load (simplified)
        try:
            import psutil
            features['cpu_load'] = psutil.cpu_percent() / 100.0
            features['memory_load'] = psutil.virtual_memory().percent / 100.0
        except Exception:
            features['cpu_load'] = 0.5
            features['memory_load'] = 0.5
        
        return features
    
    def _predict_optimal_parameters(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Predict optimal parameters using the ML model"""
        # Rule-based optimization (placeholder for ML model)
        params = self._get_default_parameters()
        
        # Adjust based on file size
        if features.get('file_size_norm', 0) > 0.7:  # Large file
            params['memory_limit'] = '2G'
            params['thread_priority'] = 'high'
            params['baksmali_flags'].extend(['-j', '2'])  # Use 2 threads for large files
        elif features.get('file_size_norm', 0) < 0.2:  # Small file
            params['memory_limit'] = '512M'
            params['thread_priority'] = 'normal'
        
        # Adjust based on system load
        cpu_load = features.get('cpu_load', 0.5)
        memory_load = features.get('memory_load', 0.5)
        
        if cpu_load > 0.8 or memory_load > 0.8:  # High system load
            params['max_concurrent'] = 1
            params['thread_priority'] = 'low'
            params['memory_limit'] = '256M'
        elif cpu_load < 0.3 and memory_load < 0.3:  # Low system load
            params['max_concurrent'] = 4
            params['thread_priority'] = 'high'
        
        # Adjust based on complexity
        complexity = features.get('complexity', 0.5)
        if complexity > 0.7:  # High complexity
            params['timeout_multiplier'] = 2.0
            params['baksmali_flags'].append('--verify-none')  # Skip verification for speed
        
        return params
    
    def _apply_safety_constraints(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply safety constraints to prevent system overload"""
        # Limit concurrent operations
        max_concurrent = params.get('max_concurrent', 4)
        params['max_concurrent'] = min(max_concurrent, 8)  # Never exceed 8
        
        # Limit memory usage
        memory_limit = params.get('memory_limit', '1G')
        if memory_limit.endswith('G'):
            value = float(memory_limit[:-1])
            if value > 4.0:  # Never use more than 4GB
                params['memory_limit'] = '4G'
        
        # Ensure timeout multiplier is reasonable
        timeout_mult = params.get('timeout_multiplier', 1.0)
        params['timeout_multiplier'] = min(max(timeout_mult, 0.5), 5.0)  # Between 0.5x and 5x
        
        return params
    
    def _get_default_parameters(self) -> Dict[str, Any]:
        """Get default optimization parameters"""
        return {
            'memory_limit': '1G',
            'thread_priority': 'normal',
            'max_concurrent': 4,
            'timeout_multiplier': 1.0,
            'baksmali_flags': [],
            'optimization_applied': False
        }
    
    def learn_from_result(self, file_info: Dict[str, Any], params: Dict[str, Any], 
                         result: Dict[str, Any]) -> None:
        """Learn from deodexing result to improve future predictions"""
        if not self.enabled:
            return
        
        try:
            # Record the optimization result
            learning_record = {
                'file_info': file_info,
                'parameters': params,
                'result': result,
                'success': result.get('status') == 'completed',
                'duration': result.get('duration', 0),
                'efficiency': self._calculate_efficiency(file_info, result)
            }
            
            self.optimization_history.append(learning_record)
            
            # Keep only recent history to prevent memory bloat
            if len(self.optimization_history) > 1000:
                self.optimization_history = self.optimization_history[-500:]
            
            # Trigger model retraining if we have enough data
            if len(self.optimization_history) > 100:
                self._update_model()
            
        except Exception as e:
            logger.error("Failed to learn from result", error=str(e))
    
    def _calculate_efficiency(self, file_info: Dict[str, Any], result: Dict[str, Any]) -> float:
        """Calculate efficiency score for a deodexing operation"""
        try:
            if result.get('status') != 'completed':
                return 0.0
            
            duration = result.get('duration', float('inf'))
            file_size_mb = file_info.get('size_mb', 1)
            
            # Efficiency = MB per second
            efficiency = file_size_mb / duration if duration > 0 else 0
            
            # Normalize to 0-1 scale (assuming max efficiency of 10 MB/s)
            return min(efficiency / 10.0, 1.0)
            
        except Exception:
            return 0.0
    
    def _update_model(self) -> None:
        """Update the ML model based on learning history"""
        try:
            # In a full implementation, this would retrain the ML model
            # For now, just update feature weights based on recent performance
            
            recent_records = self.optimization_history[-50:]  # Last 50 records
            successful_records = [r for r in recent_records if r['success']]
            
            if len(successful_records) < 10:
                return  # Not enough data
            
            # Analyze which features correlate with better efficiency
            avg_efficiency = sum(r['efficiency'] for r in successful_records) / len(successful_records)
            
            # Simple adaptive weight adjustment
            if avg_efficiency > 0.5:  # Good performance
                # Increase weight of features that are being used
                for feature in self.feature_weights:
                    self.feature_weights[feature] *= 1.01  # Slight increase
            else:  # Poor performance
                # Decrease weights to try different strategies
                for feature in self.feature_weights:
                    self.feature_weights[feature] *= 0.99  # Slight decrease
            
            # Normalize weights
            total_weight = sum(self.feature_weights.values())
            for feature in self.feature_weights:
                self.feature_weights[feature] /= total_weight
            
            logger.debug("ML model weights updated", 
                        avg_efficiency=avg_efficiency,
                        weights=self.feature_weights)
            
        except Exception as e:
            logger.error("Failed to update ML model", error=str(e))
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics and performance metrics"""
        try:
            if not self.optimization_history:
                return {'total_optimizations': 0}
            
            total_optimizations = len(self.optimization_history)
            successful_optimizations = sum(1 for r in self.optimization_history if r['success'])
            
            if successful_optimizations == 0:
                return {
                    'total_optimizations': total_optimizations,
                    'success_rate': 0.0
                }
            
            avg_efficiency = sum(r['efficiency'] for r in self.optimization_history if r['success']) / successful_optimizations
            avg_duration = sum(r['duration'] for r in self.optimization_history if r['success']) / successful_optimizations
            
            return {
                'total_optimizations': total_optimizations,
                'successful_optimizations': successful_optimizations,
                'success_rate': successful_optimizations / total_optimizations * 100,
                'average_efficiency': avg_efficiency,
                'average_duration': avg_duration,
                'current_weights': self.feature_weights.copy(),
                'enabled': self.enabled
            }
            
        except Exception as e:
            logger.error("Failed to get optimization stats", error=str(e))
            return {'error': str(e)}