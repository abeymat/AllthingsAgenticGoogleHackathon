public with sharing class StudentApplicationController {

    public class ApplicationWrapper {
        @AuraEnabled public String firstName { get; set; }
        @AuraEnabled public String lastName { get; set; }
        @AuraEnabled public String email { get; set; }
        @AuraEnabled public String phone { get; set; }
        @AuraEnabled public String schoolName { get; set; }
        @AuraEnabled public String scholarshipType { get; set; }
        @AuraEnabled public String essay { get; set; }
    }

    @AuraEnabled
    public static Id submitApplication(ApplicationWrapper appData) {
        if (appData == null) {
            throw new AuraHandledException('Application data cannot be null.');
        }

        if (String.isBlank(appData.lastName) || String.isBlank(appData.email)) {
            throw new AuraHandledException('Last Name and Email are required.');
        }

        try {
            List<Lead> existingLeads = [
                SELECT Id, FirstName, LastName, Email, Status 
                FROM Lead 
                WHERE Email = :appData.email 
                WITH USER_MODE 
                LIMIT 1
            ];

            Lead applicantLead;
            if (!existingLeads.isEmpty()) {
                applicantLead = existingLeads[0];
                applicantLead.FirstName = appData.firstName;
                applicantLead.LastName = appData.lastName;
                applicantLead.Phone = appData.phone;
                applicantLead.Company = String.isNotBlank(appData.schoolName) ? appData.schoolName : 'Prospective Student';
                applicantLead.Description = 'Scholarship Type: ' + appData.scholarshipType + '\n\nEssay:\n' + appData.essay;
                
                update as user applicantLead;
            } else {
                applicantLead = new Lead(
                    FirstName = appData.firstName,
                    LastName = appData.lastName,
                    Email = appData.email,
                    Phone = appData.phone,
                    Company = String.isNotBlank(appData.schoolName) ? appData.schoolName : 'Prospective Student',
                    LeadSource = 'Scholarship Portal',
                    Status = 'Open - Not Contacted',
                    Description = 'Scholarship Type: ' + appData.scholarshipType + '\n\nEssay:\n' + appData.essay
                );
                
                insert as user applicantLead;
            }

            return applicantLead.Id;

        } catch (Exception e) {
            throw new AuraHandledException(e.getMessage());
        }
    }

    @AuraEnabled(cacheable=true)
    public static List<String> getScholarshipTypes() {
        return new List<String>{
            'Academic Excellence Scholarship',
            'STEM Leaders Scholarship',
            'Community Impact Scholarship',
            'Arts & Humanities Grant',
            'First-Generation Student Scholarship'
        };
    }
}