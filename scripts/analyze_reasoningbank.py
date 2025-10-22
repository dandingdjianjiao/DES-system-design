"""Analyze ReasoningBank JSON storage structure"""
import json

# Load JSON
with open('C:/D/CursorProj/DES-system-design/data/memory/reasoning_bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Basic stats
total_size = len(json.dumps(data))
num_memories = len(data['memories'])

print(f"=== ReasoningBank Storage Analysis ===\n")
print(f"Total file size: {total_size/1024:.2f} KB ({total_size:,} bytes)")
print(f"Number of memories: {num_memories}")
print(f"Average size per memory: {total_size/num_memories/1024:.2f} KB\n")

# Analyze first memory
if num_memories > 0:
    mem = data['memories'][0]

    # Calculate embedding size
    if mem.get('embedding'):
        emb_dim = len(mem['embedding'])
        emb_json = json.dumps(mem['embedding'])
        emb_size = len(emb_json)
    else:
        emb_dim = 0
        emb_size = 0

    # Calculate metadata size (everything except embedding)
    mem_no_emb = {k: v for k, v in mem.items() if k != 'embedding'}
    meta_size = len(json.dumps(mem_no_emb))

    total_mem_size = emb_size + meta_size

    print(f"=== Single Memory Analysis ===")
    print(f"Title: {mem['title'][:60]}...")
    print(f"Embedding dimension: {emb_dim}")
    print(f"Embedding size: {emb_size:,} bytes ({emb_size/1024:.2f} KB)")
    print(f"Metadata size: {meta_size:,} bytes ({meta_size/1024:.2f} KB)")
    print(f"Total memory size: {total_mem_size:,} bytes")
    print(f"Embedding ratio: {emb_size/total_mem_size*100:.1f}%\n")

# Estimate space usage
total_emb_size = 0
total_meta_size = 0

for mem in data['memories']:
    if mem.get('embedding'):
        total_emb_size += len(json.dumps(mem['embedding']))
    mem_no_emb = {k: v for k, v in mem.items() if k != 'embedding'}
    total_meta_size += len(json.dumps(mem_no_emb))

print(f"=== Overall Storage Breakdown ===")
print(f"Total embedding storage: {total_emb_size/1024:.2f} KB ({total_emb_size/total_size*100:.1f}%)")
print(f"Total metadata storage: {total_meta_size/1024:.2f} KB ({total_meta_size/total_size*100:.1f}%)")
print(f"Overhead (formatting): {(total_size - total_emb_size - total_meta_size)/1024:.2f} KB")

# Projection
print(f"\n=== Scalability Projection ===")
avg_mem_size = total_size / num_memories
for target in [100, 500, 1000]:
    projected_size = avg_mem_size * target / 1024
    print(f"{target} memories: ~{projected_size:.1f} KB ({projected_size/1024:.2f} MB)")
