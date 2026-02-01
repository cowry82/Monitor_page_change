import sqlite3
import hashlib
import urllib.request
import urllib.error
from html.parser import HTMLParser
import time
import argparse
import ssl
import json
import urllib.parse
from notifiy import send_lark_notification

# Load configuration file
def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f"Failed to read configuration file: {e}")
        return None

# Resolve URL, handle relative paths
def resolve_url(base_url, relative_url):
    return urllib.parse.urljoin(base_url, relative_url)

# Get external resource content
def get_external_resource(url):
    try:
        # Create SSL context that doesn't verify certificates
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Create request object and set headers
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        # Open URL and read content
        try:
            with urllib.request.urlopen(req, timeout=10, context=context) as response:
                content = response.read().decode('utf-8', errors='replace')
            return content
        except urllib.error.HTTPError as e:
            # Even if returning 403 or other error status codes, still read content
            if hasattr(e, 'read'):
                content = e.read().decode('utf-8', errors='replace')
                print(f"External resource returned status code: {e.code}")
                return content
            else:
                print(f"Failed to get external resource: {e}")
                return None
    except Exception as e:
        print(f"Failed to get external resource: {e}")
        return None

# Monitor external resources (JS/CSS)
def monitor_external_resources(page_url, elements):
    conn = sqlite3.connect('web_monitor.db')
    c = conn.cursor()
    
    changes = []
    
    # Monitor script files
    if elements.get('scripts'):
        for script_url in elements['scripts']:
            # Resolve full URL
            full_url = resolve_url(page_url, script_url)
            # Get script content
            content = get_external_resource(full_url)
            if content:
                # Check if record exists
                c.execute('SELECT last_hash, last_content FROM external_resources WHERE resource_url = ?', (full_url,))
                result = c.fetchone()
                
                if result:
                    last_hash, last_content = result
                    current_hash = calculate_hash(content)
                    
                    if current_hash != last_hash:
                        # Detect changes
                        change_content = f'File: {full_url}\n'
                        # Simple difference analysis
                        import difflib
                        diff = list(difflib.ndiff(last_content.splitlines(), content.splitlines()))
                        
                        # Extract changed lines
                        changed_lines = []
                        for i, line in enumerate(diff):
                            if line.startswith('- ') or line.startswith('+ '):
                                changed_lines.append(line)
                                if len(changed_lines) > 10:  # Limit display lines
                                    changed_lines.append('...')
                                    break
                        
                        if changed_lines:
                            change_content += '\n'.join(changed_lines[:10])
                        else:
                            change_content += 'Content changed'
                        
                        changes.append(('script', 'modified', change_content))
                        
                        # Update record
                        c.execute('''
                            UPDATE external_resources 
                            SET last_hash = ?, last_content = ?, last_checked = ? 
                            WHERE resource_url = ?
                        ''', (current_hash, content, time.time(), full_url))
                else:
                    # New resource, add record
                    c.execute('''
                        INSERT INTO external_resources (resource_url, page_url, last_hash, last_content, last_checked) 
                        VALUES (?, ?, ?, ?, ?)
                    ''', (full_url, page_url, calculate_hash(content), content, time.time()))
                    changes.append(('script', 'added', f'New script: {full_url}'))
    
    # Monitor CSS files
    if elements.get('styles'):
        for css_url in elements['styles']:
            # Resolve full URL
            full_url = resolve_url(page_url, css_url)
            # Get CSS content
            content = get_external_resource(full_url)
            if content:
                # Check if record exists
                c.execute('SELECT last_hash, last_content FROM external_resources WHERE resource_url = ?', (full_url,))
                result = c.fetchone()
                
                if result:
                    last_hash, last_content = result
                    current_hash = calculate_hash(content)
                    
                    if current_hash != last_hash:
                        # Detect changes
                        change_content = f'File: {full_url}\n'
                        # Simple difference analysis
                        import difflib
                        diff = list(difflib.ndiff(last_content.splitlines(), content.splitlines()))
                        
                        # Extract changed lines
                        changed_lines = []
                        for i, line in enumerate(diff):
                            if line.startswith('- ') or line.startswith('+ '):
                                changed_lines.append(line)
                                if len(changed_lines) > 10:  # Limit display lines
                                    changed_lines.append('...')
                                    break
                        
                        if changed_lines:
                            change_content += '\n'.join(changed_lines[:10])
                        else:
                            change_content += 'Content changed'
                        
                        changes.append(('css', 'modified', change_content))
                        
                        # Update record
                        c.execute('''
                            UPDATE external_resources 
                            SET last_hash = ?, last_content = ?, last_checked = ? 
                            WHERE resource_url = ?
                        ''', (current_hash, content, time.time(), full_url))
                else:
                    # New resource, add record
                    c.execute('''
                        INSERT INTO external_resources (resource_url, page_url, last_hash, last_content, last_checked) 
                        VALUES (?, ?, ?, ?, ?)
                    ''', (full_url, page_url, calculate_hash(content), content, time.time()))
                    changes.append(('css', 'added', f'New CSS: {full_url}'))
    
    # Record changes
    for element_type, change_type, change_content in changes:
        c.execute('''
            INSERT INTO changes (url, change_type, change_content, change_time) 
            VALUES (?, ?, ?, ?)
        ''', (page_url, f"{element_type}_{change_type}", change_content, time.time()))
    
    conn.commit()
    conn.close()
    
    return changes

# Initialize database
def init_db():
    conn = sqlite3.connect('web_monitor.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS web_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            last_hash TEXT,
            last_content TEXT,
            last_checked TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            change_type TEXT,
            change_content TEXT,
            change_time TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS external_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_url TEXT UNIQUE,
            page_url TEXT,
            last_hash TEXT,
            last_content TEXT,
            last_checked TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Get web page content
def get_page_content(url):
    try:
        # Check if it's a local file
        if url.startswith('file://'):
            # Read local file
            file_path = url[7:]  # Remove 'file://' prefix
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return content
        else:
            # Create SSL context that doesn't verify certificates
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Create request object and set headers
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            # Open URL and read content
            try:
                with urllib.request.urlopen(req, timeout=10, context=context) as response:
                    content = response.read().decode('utf-8', errors='replace')
                return content
            except urllib.error.HTTPError as e:
                # Even if returning 403 or other error status codes, still read content
                if hasattr(e, 'read'):
                    content = e.read().decode('utf-8', errors='replace')
                    print(f"Web page returned status code: {e.code}")
                    return content
                else:
                    print(f"Failed to get web page content: {e}")
                    return None
    except Exception as e:
        print(f"Failed to get web page content: {e}")
        return None

# Custom HTML parser for extracting key elements
class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.styles = []
        self.inline_styles = []
        self.images = []
        self.image_descriptions = []
        self.text = []
        self.text_lines = []  # Store text and its line numbers
        self.html_tags = []
        self.in_script = False
        self.in_style = False
        self.in_comment = False
        self.in_image_container = False
    
    def handle_starttag(self, tag, attrs):
        # Record HTML tags and their attributes
        tag_str = f'<{tag}'
        for attr in attrs:
            tag_str += f' {attr[0]}="{attr[1]}"'
        tag_str += '>'
        self.html_tags.append(tag_str)
        
        if tag == 'script':
            self.in_script = True
            # Extract script src attribute
            for attr in attrs:
                if attr[0] == 'src':
                    self.scripts.append(attr[1])
        elif tag == 'style':
            self.in_style = True
        elif tag == 'link':
            # Extract CSS links
            rel = None
            href = None
            for attr in attrs:
                if attr[0] == 'rel':
                    rel = attr[1]
                elif attr[0] == 'href':
                    href = attr[1]
            if rel == 'stylesheet' and href:
                self.styles.append(href)
        elif tag == 'img':
            # Extract image src attribute
            for attr in attrs:
                if attr[0] == 'src':
                    self.images.append(attr[1])
        elif tag == 'div' and any(attr[0] == 'class' and 'image-container' in attr[1] for attr in attrs):
            self.in_image_container = True
    
    def handle_endtag(self, tag):
        # Record end tags
        self.html_tags.append(f'</{tag}>')
        
        if tag == 'script':
            self.in_script = False
        elif tag == 'style':
            self.in_style = False
        elif tag == 'div':
            self.in_image_container = False
    
    def handle_comment(self, data):
        # Ignore comment content
        pass
    
    def handle_data(self, data):
        if self.in_style:
            # Extract inline styles
            self.inline_styles.append(data)
        elif not self.in_script and not self.in_style:
            # Only add non-empty text
            stripped_data = data.strip()
            if stripped_data:
                self.text.append(stripped_data)
                self.text_lines.append((self.lineno, stripped_data))  # Record text and its line number
                if self.in_image_container and stripped_data.startswith('Test Image'):
                    self.image_descriptions.append(stripped_data)

# Extract key elements from web page
def extract_elements(content):
    parser = MyHTMLParser()
    parser.feed(content)
    
    # Extract all scripts
    scripts = parser.scripts
    
    # Extract all styles, deduplicate
    styles = list(set(parser.styles))
    
    # Extract all images
    images = parser.images
    
    # Extract all text content
    text = ' '.join(parser.text)
    
    # Extract inline styles
    inline_styles = ' '.join(parser.inline_styles)
    
    # Extract image descriptions
    image_descriptions = parser.image_descriptions
    
    # Extract all HTML tags
    html_tags = parser.html_tags
    
    # Extract CSS links
    css_links = []
    for tag in html_tags:
        if 'link' in tag and 'stylesheet' in tag:
            css_links.append(tag)
    
    # Extract text line information
    text_lines = parser.text_lines
    
    return {
        'scripts': scripts,
        'styles': styles,
        'css_links': css_links,
        'images': images,
        'text': text,
        'text_lines': text_lines,
        'inline_styles': inline_styles,
        'image_descriptions': image_descriptions,
        'html_tags': html_tags
    }

# Calculate content hash
def calculate_hash(content):
    return hashlib.md5(str(content).encode()).hexdigest()

# Detect changes
def detect_changes(url, current_content):
    conn = sqlite3.connect('web_monitor.db')
    c = conn.cursor()
    
    # Check if record exists
    c.execute('SELECT last_hash, last_content FROM web_pages WHERE url = ?', (url,))
    result = c.fetchone()
    
    changes = []
    
    if result:
        last_hash, last_content = result
        current_hash = calculate_hash(current_content)
        
        if current_hash != last_hash:
            # Extract current and previous elements
            current_elements = extract_elements(current_content)
            last_elements = extract_elements(last_content)
            
            # Detect script changes
            script_changes = detect_element_changes('scripts', current_elements['scripts'], last_elements['scripts'])
            changes.extend(script_changes)
            
            # Detect style changes
            style_changes = detect_element_changes('styles', current_elements['styles'], last_elements['styles'])
            changes.extend(style_changes)
            
            # Detect CSS link changes
            if current_elements['css_links'] != last_elements['css_links']:
                # Generate specific content for CSS link changes
                # Limit link count to avoid overly long output
                max_links_count = 5
                old_links = last_elements['css_links'][:max_links_count]
                new_links = current_elements['css_links'][:max_links_count]
                
                # Find differences
                added_links = [link for link in new_links if link not in old_links]
                removed_links = [link for link in old_links if link not in new_links]
                
                change_content = ''
                if added_links:
                    change_content += f'Added CSS links: {added_links}\n'
                if removed_links:
                    change_content += f'Removed CSS links: {removed_links}\n'
                
                # Find modified links
                min_len = min(len(old_links), len(new_links))
                for i in range(min_len):
                    if old_links[i] != new_links[i]:
                        change_content += f'Modified CSS link [{i}]:\nOld: {old_links[i]}\nNew: {new_links[i]}\n'
                        break  # Only show first modified link to avoid overly long output
                
                changes.append(('css_links', 'modified', change_content))
            
            # Detect image changes
            image_changes = detect_element_changes('images', current_elements['images'], last_elements['images'])
            changes.extend(image_changes)
            
            # Detect inline style changes
            if current_elements['inline_styles'] != last_elements['inline_styles']:
                # Generate specific content for inline style changes
                # Limit style length to avoid overly long output
                max_style_length = 200
                old_style = last_elements['inline_styles'][:max_style_length] + ('...' if len(last_elements['inline_styles']) > max_style_length else '')
                new_style = current_elements['inline_styles'][:max_style_length] + ('...' if len(current_elements['inline_styles']) > max_style_length else '')
                change_content = f'Old style: {old_style}\nNew style: {new_style}'
                changes.append(('inline_styles', 'modified', change_content))
            
            # Detect image description changes
            image_desc_changes = detect_element_changes('image_descriptions', current_elements['image_descriptions'], last_elements['image_descriptions'])
            changes.extend(image_desc_changes)
            
            # Detect HTML tag changes
            if current_elements['html_tags'] != last_elements['html_tags']:
                # Generate specific content for HTML tag changes
                # Limit tag count to avoid overly long output
                max_tags_count = 10
                old_tags = last_elements['html_tags'][:max_tags_count]
                new_tags = current_elements['html_tags'][:max_tags_count]
                
                # Find differences
                added_tags = [tag for tag in new_tags if tag not in old_tags]
                removed_tags = [tag for tag in old_tags if tag not in new_tags]
                
                change_content = ''
                if added_tags:
                    change_content += f'Added tags: {added_tags[:5]}...\n' if len(added_tags) > 5 else f'Added tags: {added_tags}\n'
                if removed_tags:
                    change_content += f'Removed tags: {removed_tags[:5]}...\n' if len(removed_tags) > 5 else f'Removed tags: {removed_tags}\n'
                
                # Find modified tags
                min_len = min(len(old_tags), len(new_tags))
                for i in range(min_len):
                    if old_tags[i] != new_tags[i]:
                        change_content += f'Modified tag [{i}]:\nOld: {old_tags[i]}\nNew: {new_tags[i]}\n'
                        break  # Only show first modified tag to avoid overly long output
                
                changes.append(('html_tags', 'modified', change_content))
            
            # Detect text changes
            if current_elements['text'] != last_elements['text']:
                # Extract changed core parts, only show specific changes
                old_text = last_elements['text']
                new_text = current_elements['text']
                
                # Find specific changes
                # Simple string difference analysis
                import difflib
                diff = list(difflib.ndiff(old_text.split(), new_text.split()))
                
                # Extract changed words
                old_words = []
                new_words = []
                for line in diff:
                    if line.startswith('- '):
                        old_words.append(line[2:])
                    elif line.startswith('+ '):
                        new_words.append(line[2:])
                
                # Try to find changed line numbers
                changed_lines = []
                if current_elements.get('text_lines') and last_elements.get('text_lines'):
                    # Compare text lines
                    current_text_set = set([text for (line, text) in current_elements['text_lines']])
                    last_text_set = set([text for (line, text) in last_elements['text_lines']])
                    
                    # Find added and removed text
                    added_texts = current_text_set - last_text_set
                    removed_texts = last_text_set - current_text_set
                    
                    # Find corresponding line numbers
                    for line_num, text in current_elements['text_lines']:
                        if text in added_texts:
                            changed_lines.append(f"Added line {line_num}")
                    for line_num, text in last_elements['text_lines']:
                        if text in removed_texts:
                            changed_lines.append(f"Removed line {line_num}")
                
                if old_words and new_words:
                    # Add each change separately
                    for i in range(max(len(old_words), len(new_words))):
                        old_word = old_words[i] if i < len(old_words) else ''
                        new_word = new_words[i] if i < len(new_words) else ''
                        if old_word or new_word:
                            change_content = ''
                            if old_word:
                                change_content += f'- {old_word}\n'
                            if new_word:
                                change_content += f'+ {new_word}'
                            # Add line number information
                            if changed_lines:
                                change_content += f'\nChange lines: {" ".join(changed_lines)}'
                            changes.append(('text', 'modified', change_content))
                elif old_words or new_words:
                    # Generate change info with old and new content
                    change_content = ''
                    if old_words:
                        change_content += f'- {" ".join(old_words)}\n'
                    if new_words:
                        change_content += f'+ {" ".join(new_words)}'
                    # Add line number information
                    if changed_lines:
                        change_content += f'\nChange lines: {" ".join(changed_lines)}'
                    changes.append(('text', 'modified', change_content))
                else:
                    # If direct identification fails, use simplified text
                    change_content = f'Old: {old_text}, New: {new_text}'
                    # Add line number information
                    if changed_lines:
                        change_content += f'\nChange lines: {" ".join(changed_lines)}'
                    changes.append(('text', 'modified', change_content))
            
            # Update record
            c.execute('''
                UPDATE web_pages 
                SET last_hash = ?, last_content = ?, last_checked = ? 
                WHERE url = ?
            ''', (calculate_hash(current_content), current_content, time.time(), url))
    else:
        # New page, add record
        c.execute('''
            INSERT INTO web_pages (url, last_hash, last_content, last_checked) 
            VALUES (?, ?, ?, ?)
        ''', (url, calculate_hash(current_content), current_content, time.time()))
        changes.append(('page', 'added', 'Page first monitored'))
    
    # Record changes
    for element_type, change_type, change_content in changes:
        c.execute('''
            INSERT INTO changes (url, change_type, change_content, change_time) 
            VALUES (?, ?, ?, ?)
        ''', (url, f"{element_type}_{change_type}", change_content, time.time()))
    
    conn.commit()
    conn.close()
    
    # Monitor external resources (JS/CSS)
    current_elements = extract_elements(current_content)
    external_changes = monitor_external_resources(url, current_elements)
    changes.extend(external_changes)
    
    return changes

# Detect element changes
def detect_element_changes(element_type, current_elements, last_elements):
    changes = []
    
    # Convert to sets for easier comparison
    current_set = set(filter(None, current_elements))
    last_set = set(filter(None, last_elements))
    
    # Added elements
    added = current_set - last_set
    if added:
        changes.append((element_type, 'added', f"Added: {', '.join(added)}"))
    
    # Removed elements
    removed = last_set - current_set
    if removed:
        changes.append((element_type, 'removed', f"Removed: {', '.join(removed)}"))
    
    return changes

# Display change results
def display_changes(url, changes):
    if changes:
        print(f"\n=== Changes detected ({url}) ===")
        for element_type, change_type, change_content in changes:
            if element_type == 'text' and change_type == 'modified':
                # Only show core text change content
                print(f"Text changes:")
                # Replace "- " and "+ " with "Old content: " and "New content: "
                modified_content = change_content.replace('- ', 'Old content: ').replace('+ ', 'New content: ')
                print(modified_content)
            else:
                # Simplified display for other change types
                print(f"{element_type} changes:")
                print(change_content)
            print("-------")
    else:
        print(f"\n=== No changes ({url}) ===")

# Main function
def main():
    parser = argparse.ArgumentParser(description='Monitor web page content changes')
    parser.add_argument('--url', help='Web page URL to monitor (optional, if not provided will use URLs from configuration file)')
    args = parser.parse_args()
    
    # Initialize database
    init_db()
    
    # Determine URLs to monitor
    urls_to_monitor = []
    if args.url:
        urls_to_monitor = [args.url]
    else:
        config = load_config()
        if config and config.get('monitor_urls'):
            urls_to_monitor = config['monitor_urls']
        else:
            print("No URL provided and no monitoring addresses configured in configuration file")
            return
    
    # Monitor all URLs
    for url in urls_to_monitor:
        print(f"\nMonitoring: {url}")
        content = get_page_content(url)
        if content:
            changes = detect_changes(url, content)
            display_changes(url, changes)
            if changes:
                send_lark_notification(url, changes)
        else:
            print(f"Failed to get web page content, monitoring failed: {url}")

if __name__ == "__main__":
    main()