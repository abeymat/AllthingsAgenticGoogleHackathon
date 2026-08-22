public with sharing class StudentApplicationController {

    public class ApplicationWrapper {
        @AuraEnabled public String firstName { get; set; }
        @AuraEnabled public String lastName { get; set; }
        @AuraEnabled public String email { get; set; }
        @AuraEnabled public String phone { get; set; }
        @AuraEnabled public String company { get; set; }
        @AuraEnabled public String description { get; set; }
    }

    /**
     * Submits a student application by creating a standard Lead record.
     * Standard fields are used to ensure deployment compatibility across standard Developer orgs.
     *
     * @param appData Wrapper object containing applicant details
     * @return Id of the created applicant record
     */
    @AuraEnabled
    public static Id submitApplication(ApplicationWrapper appData) {
        try {
            if (appData == null) {
                throw new AuraHandledException('Application data is required.');
            }

            if (String.isBlank(appData.lastName)) {
                throw new AuraHandledException('Last Name is a required field.');
            }

            Lead applicantLead = new Lead();
            applicantLead.FirstName = appData.firstName;
            applicantLead.LastName = appData.lastName;
            applicantLead.Email = appData.email;
            applicantLead.Phone = appData.phone;
            applicantLead.Company = String.isNotBlank(appData.company) ? appData.company : 'Student Applicant';
            applicantLead.Description = appData.description;
            applicantLead.LeadSource = 'Web/Student Application';

            SObjectAccessDecision decision = Security.stripInaccessible(
                AccessType.CREATABLE,
                new List<Lead>{ applicantLead }
            );

            List<Lead> leadsToInsert = (List<Lead>) decision.getRecords();

            if (leadsToInsert.isEmpty()) {
                throw new AuraHandledException('User does not have permission to create this record.');
            }

            insert leadsToInsert;
            return leadsToInsert[0].Id;

        } catch (AuraHandledException e) {
            throw e;
        } catch (Exception e) {
            throw new AuraHandledException('An error occurred while processing your application: ' + e.getMessage());
        }
    }
}