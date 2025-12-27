"""
Simple test server for advanced NLP endpoints
Avoids NumPy/Pandas compatibility issues by lazy loading
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import traceback
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

app = Flask(__name__)
CORS(app)

# Global instances (lazy loading)
_bert_detector = None
_fasttext_detector = None
_tfidf_detector = None

def get_bert_detector():
    """Lazy load BERT detector"""
    global _bert_detector
    if _bert_detector is None:
        try:
            from src.email_detector.bert_detector import BertEmailDetector
            _bert_detector = BertEmailDetector()
            print("[INFO] ✅ BERT detector loaded")
        except Exception as e:
            print(f"[ERROR] ❌ BERT loading failed: {e}")
            return None
    return _bert_detector

def get_fasttext_detector():
    """Lazy load FastText detector"""
    global _fasttext_detector
    if _fasttext_detector is None:
        try:
            from src.email_detector.fasttext_detector import FastTextEmailDetector
            _fasttext_detector = FastTextEmailDetector()
            # Model automatically loads in __init__
            if _fasttext_detector.model is not None:
                print("[INFO] ✅ FastText detector loaded")
            else:
                print("[WARNING] ⚠️ FastText model not found")
                return None
        except Exception as e:
            print(f"[ERROR] ❌ FastText loading failed: {e}")
            return None
    return _fasttext_detector

def get_tfidf_detector():
    """Lazy load TF-IDF detector"""
    global _tfidf_detector
    if _tfidf_detector is None:
        try:
            from src.email_detector.detector import EmailPhishingDetector
            _tfidf_detector = EmailPhishingDetector()
            print("[INFO] ✅ TF-IDF detector loaded")
        except Exception as e:
            print(f"[ERROR] ❌ TF-IDF loading failed: {e}")
            return None
    return _tfidf_detector


# ============================================
# ENDPOINTS
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0-advanced'
    }), 200


@app.route('/api/email/analyze', methods=['POST'])
def analyze_email():
    """TF-IDF baseline endpoint"""
    try:
        import time
        start_time = time.time()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email_content = data.get('email_content', '')
        email_sender = data.get('email_sender', '')
        email_subject = data.get('email_subject', '')
        
        if not email_content:
            return jsonify({'error': 'email_content is required'}), 400
        
        detector = get_tfidf_detector()
        if detector is None:
            return jsonify({'error': 'TF-IDF detector not available'}), 503
        
        if not detector.is_trained:
            return jsonify({'error': 'Model not trained'}), 503
        
        result = detector.predict_with_explanation(
            email_content, email_sender, email_subject
        )
        
        processing_time = (time.time() - start_time) * 1000
        result['processing_time_ms'] = round(processing_time, 2)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"[ERROR] TF-IDF analysis error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Analysis failed', 'message': str(e)}), 500


@app.route('/api/email/analyze/bert', methods=['POST'])
def analyze_email_bert():
    """BERT endpoint"""
    try:
        import time
        start_time = time.time()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email_content = data.get('email_content', '')
        email_subject = data.get('email_subject', '')
        
        if not email_content:
            return jsonify({'error': 'email_content is required'}), 400
        
        detector = get_bert_detector()
        if detector is None:
            return jsonify({'error': 'BERT detector not available'}), 503
        
        full_text = f"{email_subject} {email_content}".strip()
        result = detector.predict(full_text)
        
        processing_time = (time.time() - start_time) * 1000
        
        return jsonify({
            'model': 'BERT (DistilBERT)',
            'prediction': result.label,
            'confidence': float(result.confidence),
            'score': float(result.score),
            'label': result.label,
            'processing_time_ms': round(processing_time, 2)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] BERT analysis error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'BERT analysis failed', 'message': str(e)}), 500


@app.route('/api/email/analyze/fasttext', methods=['POST'])
def analyze_email_fasttext():
    """FastText endpoint"""
    try:
        import time
        start_time = time.time()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email_content = data.get('email_content', '')
        email_subject = data.get('email_subject', '')
        
        if not email_content:
            return jsonify({'error': 'email_content is required'}), 400
        
        detector = get_fasttext_detector()
        if detector is None:
            return jsonify({'error': 'FastText detector not available'}), 503
        
        full_text = f"{email_subject} {email_content}".strip()
        result = detector.predict(full_text)
        
        processing_time = (time.time() - start_time) * 1000
        
        return jsonify({
            'model': 'FastText',
            'prediction': result.label,
            'confidence': float(result.confidence),
            'score': float(result.score),
            'processing_time_ms': round(processing_time, 2)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] FastText analysis error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'FastText analysis failed', 'message': str(e)}), 500


@app.route('/api/email/analyze/hybrid', methods=['POST'])
def analyze_email_hybrid():
    """Hybrid ensemble endpoint"""
    try:
        import time
        start_time = time.time()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email_content = data.get('email_content', '')
        email_sender = data.get('email_sender', '')
        email_subject = data.get('email_subject', '')
        
        if not email_content:
            return jsonify({'error': 'email_content is required'}), 400
        
        results = {}
        predictions = []
        confidences = []
        weights = []
        
        # 1. TF-IDF
        try:
            model_start = time.time()
            tfidf_detector = get_tfidf_detector()
            if tfidf_detector and tfidf_detector.is_trained:
                tfidf_result = tfidf_detector.predict_with_explanation(
                    email_content, email_sender, email_subject
                )
                tfidf_time = (time.time() - model_start) * 1000
                
                is_phishing = tfidf_result['prediction'].lower() == 'phishing'
                results['tfidf'] = {
                    'prediction': 'phishing' if is_phishing else 'legitimate',
                    'confidence': float(tfidf_result['confidence']) / 100.0,
                    'time_ms': round(tfidf_time, 2)
                }
                predictions.append(1 if is_phishing else 0)
                confidences.append(results['tfidf']['confidence'])
                weights.append(0.3)
        except Exception as e:
            print(f"[WARNING] TF-IDF prediction failed: {e}")
        
        # 2. FastText
        try:
            model_start = time.time()
            fasttext_detector = get_fasttext_detector()
            if fasttext_detector:
                full_text = f"{email_subject} {email_content}".strip()
                ft_result = fasttext_detector.predict(full_text)
                ft_time = (time.time() - model_start) * 1000
                
                results['fasttext'] = {
                    'prediction': ft_result.label,
                    'confidence': float(ft_result.confidence),
                    'time_ms': round(ft_time, 2)
                }
                predictions.append(1 if ft_result.label == 'phishing' else 0)
                confidences.append(results['fasttext']['confidence'])
                weights.append(0.3)
        except Exception as e:
            print(f"[WARNING] FastText prediction failed: {e}")
        
        # 3. BERT
        try:
            model_start = time.time()
            bert_detector = get_bert_detector()
            if bert_detector:
                full_text = f"{email_subject} {email_content}".strip()
                bert_result = bert_detector.predict(full_text)
                bert_time = (time.time() - model_start) * 1000
                
                results['bert'] = {
                    'prediction': bert_result.label,
                    'confidence': float(bert_result.confidence),
                    'time_ms': round(bert_time, 2)
                }
                predictions.append(1 if bert_result.label == 'phishing' else 0)
                confidences.append(results['bert']['confidence'])
                weights.append(0.4)
        except Exception as e:
            print(f"[WARNING] BERT prediction failed: {e}")
        
        if not predictions:
            return jsonify({'error': 'All models failed'}), 503
        
        # Weighted average
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        weighted_sum = sum(p * c * w for p, c, w in zip(predictions, confidences, normalized_weights))
        
        final_confidence = weighted_sum
        final_prediction = 'phishing' if final_confidence >= 0.5 else 'legitimate'
        
        total_time = (time.time() - start_time) * 1000
        
        return jsonify({
            'final_prediction': final_prediction,
            'final_confidence': round(final_confidence, 4),
            'ensemble_method': 'weighted_average',
            'weights': {
                'tfidf': 0.3 if 'tfidf' in results else 0,
                'fasttext': 0.3 if 'fasttext' in results else 0,
                'bert': 0.4 if 'bert' in results else 0
            },
            'models': results,
            'models_used': len(results),
            'total_processing_time_ms': round(total_time, 2)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Hybrid analysis error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Hybrid analysis failed', 'message': str(e)}), 500


if __name__ == '__main__':
    print("="*70)
    print("🚀 Advanced NLP API Server")
    print("="*70)
    print("Endpoints:")
    print("  • POST /api/email/analyze         - TF-IDF baseline")
    print("  • POST /api/email/analyze/bert    - BERT advanced NLP")
    print("  • POST /api/email/analyze/fasttext - FastText fast detection")
    print("  • POST /api/email/analyze/hybrid  - Hybrid ensemble")
    print("  • GET  /api/health                - Health check")
    print("="*70)
    app.run(host='0.0.0.0', port=5001, debug=False)
