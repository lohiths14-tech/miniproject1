"""
Integration Service
Handles GitHub integration, IDE plugins, Slack notifications, and external platform connections
"""

import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import base64

class IntegrationType(Enum):
    """Types of integrations supported"""
    GITHUB = "github"
    SLACK = "slack" 
    DISCORD = "discord"
    VSCODE = "vscode"
    INTELLIJ = "intellij"
    CALENDAR = "calendar"

@dataclass
class IntegrationConfig:
    """Integration configuration"""
    integration_type: IntegrationType
    api_key: str
    webhook_url: Optional[str] = None
    settings: Dict = None

class IntegrationService:
    def __init__(self):
        self.active_integrations = {}
        self.notification_templates = self._load_notification_templates()
        
    def _load_notification_templates(self) -> Dict:
        """Load notification templates for different platforms"""
        return {
            "slack": {
                "assignment_graded": {
                    "text": "Assignment '{title}' has been graded",
                    "attachments": [{
                        "color": "good",
                        "fields": [
                            {"title": "Score", "value": "{score}/{max_score}", "short": True},
                            {"title": "Grade", "value": "{percentage}%", "short": True}
                        ]
                    }]
                },
                "new_assignment": {
                    "text": "New assignment available: '{title}'",
                    "attachments": [{
                        "color": "warning",
                        "fields": [
                            {"title": "Due Date", "value": "{due_date}", "short": True},
                            {"title": "Difficulty", "value": "{difficulty}", "short": True}
                        ]
                    }]
                }
            },
            "discord": {
                "assignment_graded": {
                    "embeds": [{
                        "title": "Assignment Graded 📊",
                        "description": "Your assignment '{title}' has been evaluated",
                        "color": 3447003,
                        "fields": [
                            {"name": "Score", "value": "{score}/{max_score}", "inline": True},
                            {"name": "Percentage", "value": "{percentage}%", "inline": True}
                        ]
                    }]
                }
            }
        }
    
    def setup_github_integration(self, user_id: str, github_token: str, 
                                repo_url: str) -> Dict:
        """Setup GitHub integration for code submission"""
        try:
            # Validate GitHub token
            headers = {"Authorization": f"token {github_token}"}
            response = requests.get("https://api.github.com/user", headers=headers)
            
            if response.status_code != 200:
                return {"status": "error", "message": "Invalid GitHub token"}
            
            github_user = response.json()
            
            # Store integration configuration
            integration_config = IntegrationConfig(
                integration_type=IntegrationType.GITHUB,
                api_key=github_token,
                settings={
                    "repo_url": repo_url,
                    "username": github_user["login"],
                    "user_id": github_user["id"]
                }
            )
            
            self.active_integrations[f"{user_id}_github"] = integration_config
            
            return {
                "status": "success",
                "message": "GitHub integration configured successfully",
                "github_username": github_user["login"]
            }
            
        except Exception as e:
            return {"status": "error", "message": f"GitHub integration failed: {str(e)}"}
    
    def submit_to_github(self, user_id: str, assignment_id: str, 
                        code: str, filename: str) -> Dict:
        """Submit code to GitHub repository"""
        
        integration_key = f"{user_id}_github"
        if integration_key not in self.active_integrations:
            return {"status": "error", "message": "GitHub integration not configured"}
        
        config = self.active_integrations[integration_key]
        
        try:
            headers = {"Authorization": f"token {config.api_key}"}
            repo_url = config.settings["repo_url"]
            
            # Extract owner and repo from URL
            parts = repo_url.replace("https://github.com/", "").split("/")
            owner, repo = parts[0], parts[1]
            
            # Create file content
            file_content = base64.b64encode(code.encode()).decode()
            
            # Prepare commit data
            commit_data = {
                "message": f"Submit assignment {assignment_id}",
                "content": file_content,
                "branch": "main"
            }
            
            # Check if file exists
            file_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
            existing_file = requests.get(file_url, headers=headers)
            
            if existing_file.status_code == 200:
                # File exists, update it
                commit_data["sha"] = existing_file.json()["sha"]
                commit_data["message"] = f"Update assignment {assignment_id}"
            
            # Create or update file
            response = requests.put(file_url, headers=headers, json=commit_data)
            
            if response.status_code in [200, 201]:
                return {
                    "status": "success",
                    "message": "Code submitted to GitHub successfully",
                    "commit_url": response.json()["commit"]["html_url"]
                }
            else:
                return {
                    "status": "error", 
                    "message": f"GitHub submission failed: {response.text}"
                }
                
        except Exception as e:
            return {"status": "error", "message": f"GitHub submission error: {str(e)}"}
    
    def setup_slack_integration(self, user_id: str, webhook_url: str) -> Dict:
        """Setup Slack integration for notifications"""
        try:
            # Test webhook
            test_message = {
                "text": "AI Grading System connected successfully! 🎉",
                "username": "AI Grading Bot"
            }
            
            response = requests.post(webhook_url, json=test_message)
            
            if response.status_code == 200:
                integration_config = IntegrationConfig(
                    integration_type=IntegrationType.SLACK,
                    api_key="",
                    webhook_url=webhook_url
                )
                
                self.active_integrations[f"{user_id}_slack"] = integration_config
                
                return {
                    "status": "success",
                    "message": "Slack integration configured successfully"
                }
            else:
                return {"status": "error", "message": "Invalid Slack webhook URL"}
                
        except Exception as e:
            return {"status": "error", "message": f"Slack integration failed: {str(e)}"}
    
    def send_slack_notification(self, user_id: str, notification_type: str, 
                               data: Dict) -> bool:
        """Send notification to Slack"""
        
        integration_key = f"{user_id}_slack"
        if integration_key not in self.active_integrations:
            return False
        
        config = self.active_integrations[integration_key]
        template = self.notification_templates["slack"].get(notification_type)
        
        if not template:
            return False
        
        try:
            # Format message with data
            message = {
                "text": template["text"].format(**data),
                "username": "AI Grading Bot",
                "icon_emoji": ":robot_face:"
            }
            
            if "attachments" in template:
                attachments = []
                for attachment in template["attachments"]:
                    formatted_attachment = attachment.copy()
                    if "fields" in attachment:
                        formatted_fields = []
                        for field in attachment["fields"]:
                            formatted_field = field.copy()
                            formatted_field["value"] = field["value"].format(**data)
                            formatted_fields.append(formatted_field)
                        formatted_attachment["fields"] = formatted_fields
                    attachments.append(formatted_attachment)
                message["attachments"] = attachments
            
            response = requests.post(config.webhook_url, json=message)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Slack notification failed: {e}")
            return False
    
    def setup_discord_integration(self, user_id: str, webhook_url: str) -> Dict:
        """Setup Discord integration for notifications"""
        try:
            # Test webhook
            test_message = {
                "content": "AI Grading System connected successfully! 🎉",
                "username": "AI Grading Bot"
            }
            
            response = requests.post(webhook_url, json=test_message)
            
            if response.status_code in [200, 204]:
                integration_config = IntegrationConfig(
                    integration_type=IntegrationType.DISCORD,
                    api_key="",
                    webhook_url=webhook_url
                )
                
                self.active_integrations[f"{user_id}_discord"] = integration_config
                
                return {
                    "status": "success",
                    "message": "Discord integration configured successfully"
                }
            else:
                return {"status": "error", "message": "Invalid Discord webhook URL"}
                
        except Exception as e:
            return {"status": "error", "message": f"Discord integration failed: {str(e)}"}
    
    def generate_vscode_extension_config(self, user_id: str, api_endpoint: str) -> Dict:
        """Generate VS Code extension configuration"""
        
        config = {
            "aiGradingSystem": {
                "apiEndpoint": api_endpoint,
                "userId": user_id,
                "features": {
                    "realTimeAnalysis": True,
                    "autoSubmission": False,
                    "collaborativeEditing": True,
                    "instantFeedback": True
                },
                "keybindings": [
                    {
                        "command": "aiGrading.submitCode",
                        "key": "ctrl+shift+s"
                    },
                    {
                        "command": "aiGrading.getHints",
                        "key": "ctrl+shift+h"
                    },
                    {
                        "command": "aiGrading.startCollaboration",
                        "key": "ctrl+shift+c"
                    }
                ]
            }
        }
        
        return config
    
    def generate_intellij_plugin_config(self, user_id: str, api_endpoint: str) -> Dict:
        """Generate IntelliJ plugin configuration"""
        
        config = {
            "aiGradingPlugin": {
                "serverUrl": api_endpoint,
                "userId": user_id,
                "autoAnalysis": True,
                "showComplexityMetrics": True,
                "enableCollaboration": True,
                "toolWindow": {
                    "showFeedback": True,
                    "showSuggestions": True,
                    "showMetrics": True
                }
            }
        }
        
        return config
    
    def create_calendar_integration(self, user_id: str, calendar_service: str) -> Dict:
        """Create calendar integration for assignment due dates"""
        
        # Generate calendar events for assignments
        calendar_events = [
            {
                "title": "AI Grading Assignment: Sorting Algorithms",
                "start": "2025-10-01T10:00:00",
                "end": "2025-10-01T11:00:00",
                "description": "Complete sorting algorithm implementation",
                "location": "Online - AI Grading Platform"
            },
            {
                "title": "AI Grading Assignment: Data Structures",
                "start": "2025-10-08T10:00:00", 
                "end": "2025-10-08T11:00:00",
                "description": "Implement linked list operations",
                "location": "Online - AI Grading Platform"
            }
        ]
        
        # Generate iCal format
        ical_content = self._generate_ical(calendar_events)
        
        return {
            "status": "success",
            "calendar_url": f"/api/integrations/calendar/{user_id}.ics",
            "ical_content": ical_content,
            "events_count": len(calendar_events)
        }
    
    def _generate_ical(self, events: List[Dict]) -> str:
        """Generate iCal format for calendar events"""
        
        ical_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//AI Grading System//Assignment Calendar//EN"
        ]
        
        for event in events:
            ical_lines.extend([
                "BEGIN:VEVENT",
                f"UID:{event['title'].replace(' ', '_')}_{event['start']}",
                f"DTSTART:{event['start'].replace('-', '').replace(':', '')}",
                f"DTEND:{event['end'].replace('-', '').replace(':', '')}",
                f"SUMMARY:{event['title']}",
                f"DESCRIPTION:{event['description']}",
                f"LOCATION:{event['location']}",
                "END:VEVENT"
            ])
        
        ical_lines.append("END:VCALENDAR")
        
        return "\n".join(ical_lines)
    
    def get_integration_status(self, user_id: str) -> Dict:
        """Get status of all integrations for a user"""
        
        status = {
            "github": False,
            "slack": False,
            "discord": False,
            "vscode_config": False,
            "intellij_config": False,
            "calendar": False
        }
        
        # Check active integrations
        for key in self.active_integrations:
            if key.startswith(user_id):
                integration_type = key.split("_")[1]
                if integration_type in status:
                    status[integration_type] = True
        
        return {
            "user_id": user_id,
            "integrations": status,
            "total_active": sum(status.values()),
            "available_integrations": len(status)
        }
    
    def remove_integration(self, user_id: str, integration_type: str) -> Dict:
        """Remove an integration"""
        
        integration_key = f"{user_id}_{integration_type}"
        
        if integration_key in self.active_integrations:
            del self.active_integrations[integration_key]
            return {
                "status": "success",
                "message": f"{integration_type.title()} integration removed successfully"
            }
        else:
            return {
                "status": "error",
                "message": f"{integration_type.title()} integration not found"
            }
    
    def notify_assignment_graded(self, user_id: str, assignment_data: Dict) -> Dict:
        """Send notifications across all configured platforms"""
        
        results = {}
        
        # Slack notification
        if f"{user_id}_slack" in self.active_integrations:
            slack_success = self.send_slack_notification(user_id, "assignment_graded", assignment_data)
            results["slack"] = "success" if slack_success else "failed"
        
        # Discord notification  
        if f"{user_id}_discord" in self.active_integrations:
            discord_success = self.send_discord_notification(user_id, "assignment_graded", assignment_data)
            results["discord"] = "success" if discord_success else "failed"
        
        return {
            "notifications_sent": len(results),
            "results": results
        }
    
    def send_discord_notification(self, user_id: str, notification_type: str, data: Dict) -> bool:
        """Send notification to Discord"""
        
        integration_key = f"{user_id}_discord"
        if integration_key not in self.active_integrations:
            return False
        
        config = self.active_integrations[integration_key]
        template = self.notification_templates["discord"].get(notification_type)
        
        if not template:
            return False
        
        try:
            message = {
                "username": "AI Grading Bot",
                "avatar_url": "https://example.com/bot-avatar.png"
            }
            
            if "embeds" in template:
                embeds = []
                for embed in template["embeds"]:
                    formatted_embed = {
                        "title": embed["title"],
                        "description": embed["description"].format(**data),
                        "color": embed["color"]
                    }
                    
                    if "fields" in embed:
                        formatted_fields = []
                        for field in embed["fields"]:
                            formatted_field = {
                                "name": field["name"],
                                "value": field["value"].format(**data),
                                "inline": field.get("inline", False)
                            }
                            formatted_fields.append(formatted_field)
                        formatted_embed["fields"] = formatted_fields
                    
                    embeds.append(formatted_embed)
                
                message["embeds"] = embeds
            
            response = requests.post(config.webhook_url, json=message)
            return response.status_code in [200, 204]
            
        except Exception as e:
            print(f"Discord notification failed: {e}")
            return False

# Global instance
integration_service = IntegrationService()