import random
import string
import json
import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import hashlib
import requests
import logging

# Configure logging
logging.basicConfig(filename='password_generator.log', level=logging.INFO)

class PasswordGenerator:
    def __init__(self):
        self.password_history = []
        self.character_sets = {
            'lowercase': string.ascii_lowercase,
            'uppercase': string.ascii_uppercase,
            'digits': string.digits,
            'special': string.punctuation
        }

    def generate_password(self, length=12, use_uppercase=True, use_numbers=True, use_special=True):
        """
        Generates a random password with specified criteria.
        
        Args:
            length (int): Length of the password (8-128)
            use_uppercase (bool): Include uppercase letters
            use_numbers (bool): Include numbers
            use_special (bool): Include special characters
            
        Returns:
            str: Generated password
        """
        # Validate length
        if not 8 <= length <= 128:
            raise ValueError("Password length must be between 8 and 128 characters")
            
        # Build character set based on criteria
        chars = self.character_sets['lowercase']
        required_chars = []
        
        if use_uppercase:
            chars += self.character_sets['uppercase']
            required_chars.append(random.choice(self.character_sets['uppercase']))
        if use_numbers:
            chars += self.character_sets['digits']
            required_chars.append(random.choice(self.character_sets['digits']))
        if use_special:
            chars += self.character_sets['special']
            required_chars.append(random.choice(self.character_sets['special']))
            
        # Ensure we have at least one of each required character type
        password = required_chars.copy()
        password.append(random.choice(self.character_sets['lowercase']))
        
        # Fill remaining length
        remaining_length = length - len(password)
        if remaining_length > 0:
            password.extend(random.choice(chars) for _ in range(remaining_length))
            
        # Shuffle to ensure randomness
        random.shuffle(password)
        
        generated_password = ''.join(password)
        
        # Store in history
        self.password_history.append({
            'password': generated_password,
            'timestamp': datetime.now().isoformat(),
            'criteria': {
                'length': length,
                'use_uppercase': use_uppercase,
                'use_numbers': use_numbers,
                'use_special': use_special
            }
        })
        
        return generated_password
        
    def generate_multiple_passwords(self, count=5, **kwargs):
        """
        Generates multiple passwords with the same criteria.
        
        Args:
            count (int): Number of passwords to generate
            **kwargs: Same as generate_password arguments
            
        Returns:
            list: List of generated passwords
        """
        return [self.generate_password(**kwargs) for _ in range(count)]
        
    def evaluate_password_strength(self, password):
        """
        Evaluates the strength of a password.
        
        Args:
            password (str): Password to evaluate
            
        Returns:
            dict: Dictionary containing score (0-100), rating, and suggestions
        """
        result = {
            'score': 0,
            'rating': 'Very Weak',
            'suggestions': []
        }
        
        # Length check
        length = len(password)
        if length >= 12:
            result['score'] += 30
        elif length >= 8:
            result['score'] += 20
        else:
            result['suggestions'].append("Password is too short (minimum 8 characters)")
            
        # Character variety
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in self.character_sets['special'] for c in password)
        
        if has_lower:
            result['score'] += 10
        else:
            result['suggestions'].append("Add lowercase letters")
            
        if has_upper:
            result['score'] += 10
        else:
            result['suggestions'].append("Add uppercase letters")
            
        if has_digit:
            result['score'] += 10
        else:
            result['suggestions'].append("Add numbers")
            
        if has_special:
            result['score'] += 10
        else:
            result['suggestions'].append("Add special characters")
            
        # Common patterns check
        common_patterns = [
            '123', 'abc', 'qwerty', 'password', 'admin', 'welcome'
        ]
        
        lower_pass = password.lower()
        if any(pattern in lower_pass for pattern in common_patterns):
            result['score'] -= 20
            result['suggestions'].append("Avoid common patterns")
            
        # Sequential characters check
        has_sequence = False
        for i in range(len(password) - 2):
            if (ord(password[i+1]) == ord(password[i]) + 1 and 
                ord(password[i+2]) == ord(password[i+1]) + 1):
                has_sequence = True
                break
                
        if has_sequence:
            result['score'] -= 15
            result['suggestions'].append("Avoid sequential characters")
            
        # Repeated characters check
        has_repeat = any(password[i] == password[i+1] == password[i+2] 
                        for i in range(len(password) - 2))
        if has_repeat:
            result['score'] -= 15
            result['suggestions'].append("Avoid repeated characters")
            
        # Determine rating
        if result['score'] >= 80:
            result['rating'] = 'Very Strong'
        elif result['score'] >= 60:
            result['rating'] = 'Strong'
        elif result['score'] >= 40:
            result['rating'] = 'Good'
        elif result['score'] >= 20:
            result['rating'] = 'Weak'
        else:
            result['rating'] = 'Very Weak'
            
        # Check against breached passwords (requires internet)
        try:
            sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
            prefix = sha1_hash[:5]
            response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
            
            if response.status_code == 200:
                suffixes = (line.split(':') for line in response.text.splitlines())
                for suffix, count in suffixes:
                    if sha1_hash[5:] == suffix:
                        result['score'] = 0
                        result['rating'] = 'Compromised'
                        result['suggestions'].append(
                            f"This password has been found in {count} data breaches. DO NOT USE IT!")
                        break
        except requests.RequestException:
            pass
            
        return result
        
    def export_passwords(self, format_type='json', file_path=None):
        """
        Exports password history to a file.
        
        Args:
            format_type (str): 'json' or 'csv'
            file_path (str): Path to save file (None for auto-generated)
            
        Returns:
            str: Path to saved file
        """
        if not self.password_history:
            raise ValueError("No passwords to export")
            
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"passwords_{timestamp}.{format_type}"
            
        try:
            if format_type.lower() == 'json':
                with open(file_path, 'w') as f:
                    json.dump(self.password_history, f, indent=2)
            elif format_type.lower() == 'csv':
                with open(file_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['password', 'timestamp', 'criteria'])
                    writer.writeheader()
                    for entry in self.password_history:
                        writer.writerow(entry)
            else:
                raise ValueError("Unsupported format type")
                
            logging.info(f"Exported passwords to {file_path}")
            return file_path
            
        except Exception as e:
            logging.error(f"Failed to export passwords: {str(e)}")
            raise
            
    def import_passwords(self, file_path):
        """
        Imports passwords from a file.
        
        Args:
            file_path (str): Path to import file
            
        Returns:
            int: Number of passwords imported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            if file_path.lower().endswith('.json'):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if not isinstance(data, list):
                        raise ValueError("Invalid JSON format")
                    self.password_history.extend(data)
                    return len(data)
                    
            elif file_path.lower().endswith('.csv'):
                with open(file_path, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    imported = 0
                    for row in reader:
                        try:
                            entry = {
                                'password': row['password'],
                                'timestamp': row.get('timestamp', datetime.now().isoformat()),
                                'criteria': json.loads(row.get('criteria', '{}'))
                            }
                            self.password_history.append(entry)
                            imported += 1
                        except (KeyError, json.JSONDecodeError):
                            continue
                    return imported
            else:
                raise ValueError("Unsupported file format")
                
        except Exception as e:
            logging.error(f"Failed to import passwords: {str(e)}")
            raise


class PasswordGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("600x500")
        
        self.generator = PasswordGenerator()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Password criteria frame
        criteria_frame = ttk.LabelFrame(main_frame, text="Password Criteria", padding="10")
        criteria_frame.pack(fill=tk.X, pady=5)
        
        # Length
        ttk.Label(criteria_frame, text="Length (8-128):").grid(row=0, column=0, sticky=tk.W)
        self.length_var = tk.IntVar(value=12)
        self.length_spin = ttk.Spinbox(criteria_frame, from_=8, to=128, textvariable=self.length_var, width=5)
        self.length_spin.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Uppercase
        self.uppercase_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(criteria_frame, text="Include Uppercase Letters", 
                       variable=self.uppercase_var).grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        # Numbers
        self.numbers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(criteria_frame, text="Include Numbers", 
                       variable=self.numbers_var).grid(row=2, column=0, columnspan=2, sticky=tk.W)
        
        # Special characters
        self.special_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(criteria_frame, text="Include Special Characters", 
                       variable=self.special_var).grid(row=3, column=0, columnspan=2, sticky=tk.W)
        
        # Number of passwords
        ttk.Label(criteria_frame, text="Number to generate:").grid(row=4, column=0, sticky=tk.W)
        self.count_var = tk.IntVar(value=1)
        self.count_spin = ttk.Spinbox(criteria_frame, from_=1, to=20, textvariable=self.count_var, width=5)
        self.count_spin.grid(row=4, column=1, sticky=tk.W, padx=5)
        
        # Generate button
        generate_btn = ttk.Button(main_frame, text="Generate Passwords", command=self.generate_passwords)
        generate_btn.pack(pady=10)
        
        # Password display
        self.password_text = tk.Text(main_frame, height=10, width=60, wrap=tk.WORD)
        self.password_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Strength indicator
        strength_frame = ttk.Frame(main_frame)
        strength_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(strength_frame, text="Strength:").pack(side=tk.LEFT)
        self.strength_var = tk.StringVar(value="Not evaluated")
        ttk.Label(strength_frame, textvariable=self.strength_var).pack(side=tk.LEFT, padx=5)
        
        # Menu
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export Passwords...", command=self.export_passwords)
        file_menu.add_command(label="Import Passwords...", command=self.import_passwords)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        self.root.config(menu=menubar)
        
    def generate_passwords(self):
        try:
            count = self.count_var.get()
            length = self.length_var.get()
            use_upper = self.uppercase_var.get()
            use_numbers = self.numbers_var.get()
            use_special = self.special_var.get()
            
            self.password_text.delete(1.0, tk.END)
            
            if count == 1:
                password = self.generator.generate_password(
                    length=length,
                    use_uppercase=use_upper,
                    use_numbers=use_numbers,
                    use_special=use_special
                )
                self.password_text.insert(tk.END, password)
                
                # Evaluate strength
                strength = self.generator.evaluate_password_strength(password)
                self.strength_var.set(f"{strength['rating']} ({strength['score']}/100)")
                
                # Show suggestions if any
                if strength['suggestions']:
                    messagebox.showinfo(
                        "Password Suggestions",
                        "\n".join(strength['suggestions'])
                    )
            else:
                passwords = self.generator.generate_multiple_passwords(
                    count=count,
                    length=length,
                    use_uppercase=use_upper,
                    use_numbers=use_numbers,
                    use_special=use_special
                )
                
                for i, password in enumerate(passwords, 1):
                    self.password_text.insert(tk.END, f"{i}. {password}\n")
                    
                self.strength_var.set("Multiple passwords generated")
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def export_passwords(self):
        if not self.generator.password_history:
            messagebox.showwarning("Warning", "No passwords to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv")]
        )
        
        if file_path:
            try:
                format_type = 'json' if file_path.lower().endswith('.json') else 'csv'
                saved_path = self.generator.export_passwords(format_type, file_path)
                messagebox.showinfo("Success", f"Passwords exported to:\n{saved_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export passwords:\n{str(e)}")
                
    def import_passwords(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv")]
        )
        
        if file_path:
            try:
                count = self.generator.import_passwords(file_path)
                messagebox.showinfo("Success", f"Successfully imported {count} passwords")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import passwords:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorGUI(root)
    root.mainloop()