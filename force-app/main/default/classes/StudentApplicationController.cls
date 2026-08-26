public with sharing class StudentApplicationController {

    public class ApplicationResult {
        @AuraEnabled public Boolean isSuccess { get; set; }
        @AuraEnabled public String recordId { get; set; }
        @AuraEnabled public String message { get; set; }

        public ApplicationResult(Boolean isSuccess, String recordId, String message) {
            this.isSuccess = isSuccess;
            this.recordId = recordId;
            this.message = message;
        }
    }

    /**
     * Submits a student application by creating a Lead record.
     * Uses standard fields to ensure DE org schema compatibility.
     */
    @AuraEnabled
    public static ApplicationResult submitApplication(String firstName, String lastName, String email, String phone, String company) {
        try {
            if (String.isBlank(lastName)) {
                throw new AuraHandledException('Last Name is a required field.');
            }
            if (String.isBlank(email)) {
                throw new AuraHandledException('Email is a required field.');
            }

            Lead newApplicant = new Lead(
                FirstName = firstName,
                LastName = lastName,
                Email = email,
                Phone = phone,
                Company = String.isNotBlank(company) ? company : 'Student Applicant',
                LeadSource = 'Web',
                Status = 'Open - Not Contacted'
            );

            // Security stripping for secure creation
            SObjectAccessDecision securityDecision = Security.stripInaccessible(
                AccessType.CREATABLE,
                new List<Lead>{ newApplicant }
            );

            List<Lead> leadsToInsert = securityDecision.getRecords();
            if (!leadsToInsert.isEmpty()) {
                insert leadsToInsert;
                return new ApplicationResult(true, leadsToInsert[0].Id, 'Application submitted successfully.');
            } else {
                throw new AuraHandledException('Insufficient permissions to submit application.');
            }
        } catch (AuraHandledException e) {
            throw e;
        } catch (Exception ex) {
            throw new AuraHandledException('Error submitting application: ' + ex.getMessage());
        }
    }

    /**
     * Retrieves application status details by Lead Record Id.
     */
    @AuraEnabled(cacheable=true)
    public static Lead getApplicationStatus(String recordId) {
        if (String.isBlank(recordId)) {
            return null;
        }

        List<Lead> leads = [
            SELECT Id, FirstName, LastName, Email, Phone, Company, Status, CreatedDate
            FROM Lead
            WHERE Id = :recordId
            WITH USER_MODE
            LIMIT 1
        ];

        return leads.isEmpty() ? null : leads[0];
    }
}