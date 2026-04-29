#!/usr/bin/env python3
"""
Banner Maker 로컬 서버
- 정적 파일 서빙 (기존 python3 -m http.server 대체)
- POST /api/calibration 으로 학습 데이터 JSON 파일 저장
사용법: cd banner_maker && python3 server.py
"""

import http.server
import json
import os

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class BannerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_POST(self):
        if self.path == '/api/calibration':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                banner_id = data.get('banner_id')
                if not banner_id:
                    self._respond(400, {'error': 'banner_id 필수'})
                    return

                filepath = os.path.join(BASE_DIR, 'config', 'banners', f'{banner_id}_calibration.json')

                # 기존 파일이 있으면 읽어서 samples에 추가
                existing = {'banner_id': banner_id, 'samples': [], 'average': {}}
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing = json.load(f)

                # 새 샘플 추가
                sample = data.get('sample', {})
                existing['samples'].append(sample)

                # 평균 재계산
                samples = existing['samples']
                if samples:
                    avg_scale_delta = sum(s.get('scale_delta', 0) for s in samples) / len(samples)
                    avg_offset_y_delta = sum(s.get('offset_y_delta', 0) for s in samples) / len(samples)
                    avg_offset_x_delta = sum(s.get('offset_x_delta', 0) for s in samples) / len(samples)
                    existing['average'] = {
                        'scale_delta': round(avg_scale_delta, 4),
                        'offset_y_delta': round(avg_offset_y_delta, 2),
                        'offset_x_delta': round(avg_offset_x_delta, 2),
                        'sample_count': len(samples)
                    }

                # 파일 저장
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(existing, f, ensure_ascii=False, indent=2)

                self._respond(200, {'ok': True, 'sample_count': len(samples), 'average': existing['average']})

            except json.JSONDecodeError:
                self._respond(400, {'error': 'JSON 파싱 실패'})
        else:
            self._respond(404, {'error': 'Not found'})

    def _respond(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    print(f'Banner Maker 서버 시작: http://localhost:{PORT}/')
    print(f'베이스 디렉토리: {BASE_DIR}')
    print('종료: Ctrl+C')
    server = http.server.HTTPServer(('', PORT), BannerHandler)
    server.serve_forever()
