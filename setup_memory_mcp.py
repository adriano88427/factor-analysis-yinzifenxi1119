#!/usr/bin/env python3
import os
import json

# Create directories
memory_dir = "C:\\Users\\NINGMEI\\Documents\\Cline\\MCP\\memory"
os.makedirs(memory_dir, exist_ok=True)
print(f"Created directory: {memory_dir}")

# Create a simple memory server script
memory_server_script = '''#!/usr/bin/env python3
"""
Simple Memory MCP Server
A basic implementation of persistent memory using a local knowledge graph.
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional
import re

class MemoryServer:
    def __init__(self, memory_file: str = "memory.jsonl"):
        self.memory_file = memory_file
        self.entities = {}
        self.relations = []
        self.load_memory()
    
    def load_memory(self):
        """Load memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            if data['type'] == 'entity':
                                self.entities[data['name']] = data
                            elif data['type'] == 'relation':
                                self.relations.append(data)
            except Exception as e:
                print(f"Error loading memory: {e}", file=sys.stderr)
    
    def save_memory(self):
        """Save memory to file"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                for entity in self.entities.values():
                    json.dump({'type': 'entity', **entity}, f, ensure_ascii=False)
                    f.write('\\n')
                for relation in self.relations:
                    json.dump({'type': 'relation', **relation}, f, ensure_ascii=False)
                    f.write('\\n')
        except Exception as e:
            print(f"Error saving memory: {e}", file=sys.stderr)
    
    def create_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple new entities in the knowledge graph"""
        result = []
        for entity_data in entities:
            name = entity_data['name']
            if name not in self.entities:
                entity = {
                    'name': name,
                    'entityType': entity_data.get('entityType', 'unknown'),
                    'observations': entity_data.get('observations', [])
                }
                self.entities[name] = entity
                result.append(entity)
        self.save_memory()
        return {'created': result}
    
    def create_relations(self, relations: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create multiple new relations between entities"""
        result = []
        for relation_data in relations:
            relation = {
                'from': relation_data['from'],
                'to': relation_data['to'],
                'relationType': relation_data['relationType']
            }
            if relation not in self.relations:
                self.relations.append(relation)
                result.append(relation)
        self.save_memory()
        return {'created': result}
    
    def add_observations(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add new observations to existing entities"""
        result = {}
        for obs_data in observations:
            entity_name = obs_data['entityName']
            if entity_name in self.entities:
                new_observations = obs_data['contents']
                existing_observations = self.entities[entity_name]['observations']
                added = []
                for obs in new_observations:
                    if obs not in existing_observations:
                        existing_observations.append(obs)
                        added.append(obs)
                result[entity_name] = added
                self.save_memory()
        return {'added': result}
    
    def read_graph(self) -> Dict[str, Any]:
        """Read the entire knowledge graph"""
        return {
            'entities': list(self.entities.values()),
            'relations': self.relations
        }
    
    def search_nodes(self, query: str) -> Dict[str, Any]:
        """Search for nodes based on query"""
        query_lower = query.lower()
        matches = []
        
        for entity in self.entities.values():
            # Search in name, type, and observations
            if (query_lower in entity['name'].lower() or 
                query_lower in entity['entityType'].lower() or
                any(query_lower in obs.lower() for obs in entity['observations'])):
                
                # Find relations for this entity
                entity_relations = [
                    r for r in self.relations 
                    if r['from'] == entity['name'] or r['to'] == entity['name']
                ]
                
                matches.append({
                    'entity': entity,
                    'relations': entity_relations
                })
        
        return {'matches': matches}

def main():
    memory_file = os.environ.get('MEMORY_FILE_PATH', 'memory.jsonl')
    server = MemoryServer(memory_file)
    
    print("Memory MCP Server starting...", file=sys.stderr)
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line.strip())
            method = request.get('method')
            params = request.get('params', {})
            
            if method == 'initialize':
                response = {
                    'jsonrpc': '2.0',
                    'id': request.get('id'),
                    'result': {
                        'protocolVersion': '2024-11-05',
                        'capabilities': {
                            'tools': {}
                        },
                        'serverInfo': {
                            'name': 'memory-server',
                            'version': '1.0.0'
                        }
                    }
                }
            elif method == 'tools/list':
                response = {
                    'jsonrpc': '2.0',
                    'id': request.get('id'),
                    'result': {
                        'tools': [
                            {
                                'name': 'create_entities',
                                'description': 'Create multiple new entities in the knowledge graph',
                                'inputSchema': {
                                    'type': 'object',
                                    'properties': {
                                        'entities': {
                                            'type': 'array',
                                            'items': {
                                                'type': 'object',
                                                'properties': {
                                                    'name': {'type': 'string'},
                                                    'entityType': {'type': 'string'},
                                                    'observations': {
                                                        'type': 'array',
                                                        'items': {'type': 'string'}
                                                    }
                                                },
                                                'required': ['name']
                                            }
                                        }
                                    },
                                    'required': ['entities']
                                }
                            },
                            {
                                'name': 'create_relations',
                                'description': 'Create multiple new relations between entities',
                                'inputSchema': {
                                    'type': 'object',
                                    'properties': {
                                        'relations': {
                                            'type': 'array',
                                            'items': {
                                                'type': 'object',
                                                'properties': {
                                                    'from': {'type': 'string'},
                                                    'to': {'type': 'string'},
                                                    'relationType': {'type': 'string'}
                                                },
                                                'required': ['from', 'to', 'relationType']
                                            }
                                        }
                                    },
                                    'required': ['relations']
                                }
                            },
                            {
                                'name': 'add_observations',
                                'description': 'Add new observations to existing entities',
                                'inputSchema': {
                                    'type': 'object',
                                    'properties': {
                                        'observations': {
                                            'type': 'array',
                                            'items': {
                                                'type': 'object',
                                                'properties': {
                                                    'entityName': {'type': 'string'},
                                                    'contents': {
                                                        'type': 'array',
                                                        'items': {'type': 'string'}
                                                    }
                                                },
                                                'required': ['entityName', 'contents']
                                            }
                                        }
                                    },
                                    'required': ['observations']
                                }
                            },
                            {
                                'name': 'read_graph',
                                'description': 'Read the entire knowledge graph',
                                'inputSchema': {'type': 'object'}
                            },
                            {
                                'name': 'search_nodes',
                                'description': 'Search for nodes based on query',
                                'inputSchema': {
                                    'type': 'object',
                                    'properties': {
                                        'query': {'type': 'string'}
                                    },
                                    'required': ['query']
                                }
                            }
                        ]
                    }
                }
            elif method == 'tools/call':
                tool_name = params.get('name')
                arguments = params.get('arguments', {})
                
                if tool_name == 'create_entities':
                    result = server.create_entities(arguments.get('entities', []))
                elif tool_name == 'create_relations':
                    result = server.create_relations(arguments.get('relations', []))
                elif tool_name == 'add_observations':
                    result = server.add_observations(arguments.get('observations', []))
                elif tool_name == 'read_graph':
                    result = server.read_graph()
                elif tool_name == 'search_nodes':
                    result = server.search_nodes(arguments.get('query', ''))
                else:
                    result = {'error': f'Unknown tool: {tool_name}'}
                
                response = {
                    'jsonrpc': '2.0',
                    'id': request.get('id'),
                    'result': {
                        'content': [
                            {
                                'type': 'text',
                                'text': json.dumps(result, ensure_ascii=False, indent=2)
                            }
                        ]
                    }
                }
            else:
                response = {
                    'jsonrpc': '2.0',
                    'id': request.get('id'),
                    'error': {'code': -32601, 'message': 'Method not found'}
                }
            
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            continue

if __name__ == '__main__':
    main()
'''

    # Write the memory server script
    script_path = os.path.join(memory_dir, "memory_server.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(memory_server_script)
    print(f"Created memory server script: {script_path}")

print("Memory MCP server setup complete!")
