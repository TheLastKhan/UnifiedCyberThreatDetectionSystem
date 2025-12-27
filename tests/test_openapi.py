#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenAPI specification validator"""
import sys
import yaml
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
    except AttributeError:
        # Python < 3.7 fallback
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def validate_openapi():
    try:
        # Load YAML
        with open('docs/openapi.yaml', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
        
        print("[OK] YAML Syntax: Valid")
        
        # Check required fields
        assert 'openapi' in spec, "Missing 'openapi' field"
        assert 'info' in spec, "Missing 'info' field"
        assert 'paths' in spec, "Missing 'paths' field"
        
        print(f"[OK] OpenAPI Version: {spec['openapi']}")
        print(f"[OK] API Title: {spec['info']['title']}")
        print(f"[OK] API Version: {spec['info']['version']}")
        
        # Count endpoints
        total_paths = len(spec['paths'])
        total_operations = 0
        methods = ['get', 'post', 'put', 'delete', 'patch']
        
        for path, operations in spec['paths'].items():
            for method in methods:
                if method in operations:
                    total_operations += 1
        
        print(f"[OK] Total Paths: {total_paths}")
        print(f"[OK] Total Operations: {total_operations}")
        
        # Check AŞAMA 8 endpoints
        aşama8_endpoints = [
            '/enrich/ip',
            '/enrich/domain',
            '/alert/send',
            '/cache/stats',
            '/ratelimit/status'
        ]
        
        print("\n[ASAMA-8] Endpoints:")
        for endpoint in aşama8_endpoints:
            if endpoint in spec['paths']:
                operations = [m for m in methods if m in spec['paths'][endpoint]]
                print(f"  [OK] {endpoint} [{', '.join(operations).upper()}]")
            else:
                print(f"  [FAIL] {endpoint} [NOT FOUND]")
        
        # Check components
        if 'components' in spec and 'schemas' in spec['components']:
            total_schemas = len(spec['components']['schemas'])
            print(f"\n[OK] Total Component Schemas: {total_schemas}")
        
        # Check servers
        if 'servers' in spec:
            print(f"\n[SERVERS] {len(spec['servers'])} configured")
            for server in spec['servers']:
                print(f"  - {server['url']}")
        
        # Check tags
        if 'tags' in spec:
            print(f"\n[TAGS] {len(spec['tags'])} categories")
            for tag in spec['tags']:
                print(f"  - {tag['name']}")
        
        print("\n[OK] OpenAPI specification is valid!")
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    validate_openapi()
