# 🔐 Password Generator

A comprehensive and secure password generator application with advanced features, built with Python and Tkinter.

## 🌟 Features

| Feature | Description |
|---------|-------------|
| **Customizable Generation** | Generate passwords with customizable length (8-128 chars) and character sets |
| **Strength Evaluation** | Real-time password strength assessment with detailed feedback |
| **Batch Generation** | Generate multiple passwords at once with consistent criteria |
| **Import/Export** | Save and load password collections in JSON or CSV format |
| **Security Checks** | Checks against common patterns and known breached passwords |
| **User-Friendly UI** | Clean graphical interface with intuitive controls |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Tkinter (usually included with Python)

### Installation
```bash
git clone https://github.com/yourusername/password-generator.git
cd password-generator
pip install -r requirements.txt
```

### Running the Application
```bash
python password_generator.py
```

## 🛠️ Usage

1. **Set your criteria**:
   - Choose password length (8-128 characters)
   - Select character types (uppercase, numbers, special chars)
   - Specify how many passwords to generate

2. **Generate passwords**:
   - Click "Generate Passwords" button
   - View generated passwords in the text area
   - See strength rating for single passwords

3. **Save/load passwords**:
   - Use File menu to export to JSON/CSV
   - Import previously generated passwords

## 📊 Password Strength Metrics

The generator evaluates passwords based on:

```python
{
    "length": "12+ characters ideal",
    "character_variety": "Lowercase, uppercase, numbers, symbols",
    "common_patterns": "Avoids sequential/repeated characters",
    "breach_check": "Checks against known compromised passwords"
}
```

## 📦 File Formats

### JSON Export Example
```json
[
    {
        "password": "xK$8pL@2qZ#9",
        "timestamp": "2023-07-20T14:32:10.123456",
        "criteria": {
            "length": 12,
            "use_uppercase": true,
            "use_numbers": true,
            "use_special": true
        }
    }
]
```

### CSV Export Example
```
password,timestamp,criteria
"xK$8pL@2qZ#9","2023-07-20T14:32:10.123456","{'length': 12, 'use_uppercase': true, 'use_numbers': true, 'use_special': true}"
```

## 🛡️ Security Features

- Uses cryptographically secure random generation (`secrets` module)
- No network transmission of generated passwords
- Local storage only when explicitly exported
- Checks against [Have I Been Pwned](https://haveibeenpwned.com/) API (optional)
