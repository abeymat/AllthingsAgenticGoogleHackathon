public with sharing class StudentApplicationController {

    /**
     * Wrapper class to hold Student Application details using standard Lead fields.
     */
    public class ApplicationData {
        @AuraEnabled public String firstName { get; set; }
        @AuraEnabled public String lastName { get; set; }
        @AuraEnabled public String email { get; set; }
        @AuraEnabled public String phone { get; set; }
        @AuraEnabled public String company { get; set; }
        @AuraEnabled public String description { get; set; }
    }

    /**
     * Submits a student application by creating a standard Lead record.
     * 
     * @param appData ApplicationData object containing applicant information
     * @return Id of the created Lead record
     */
    @AuraEnabled
    public static Id submitStudentApplication(ApplicationData appData) {
        try {
            if (appData == null) {
                throw new AuraHandledException('Application data cannot be null.');
            }

            if (String.isBlank(appData.lastName)) {
                throw new AuraHandledException('Last Name is required to submit an application.');
            }

            if (String.isBlank(appData.email)) {
                throw new AuraHandledException('Email is required to submit an application.');
            }

            // Enforce Object Level Security
            if (!Schema.sObjectType.Lead.isCreateable()) {
                throw new AuraHandledException('Insufficient permissions to submit an application.');
            }

            // Enforce Field Level Security
            if (
                !Schema.sObjectType.Lead.fields.FirstName.isCreateable() ||
                !Schema.sObjectType.Lead.fields.LastName.isCreateable() ||
                !Schema.sObjectType.Lead.fields.Email.isCreateable() ||
                !Schema.sObjectType.Lead.fields.Phone.isCreateable() ||
                !Schema.sObjectType.Lead.fields.Company.isCreateable() ||
                !Schema.sObjectType.Lead.fields.Description.isCreateable() ||
                !Schema.sObjectType.Lead.fields.LeadSource.isCreateable() ||
                !Schema.sObjectType.Lead.fields.Status.isCreateable()
            ) {
                throw new AuraHandledException('Insufficient field permissions to submit application.');
            }

            Lead newApplicant = new Lead();
            newApplicant.FirstName = appData.firstName;
            newApplicant.LastName = appData.lastName;
            newApplicant.Email = appData.email;
            newApplicant.Phone = appData.phone;
            // Lead.Company is a required standard field in Salesforce
            newApplicant.Company = String.isNotBlank(appData.company) ? appData.company : 'Student Applicant';
            newApplicant.Description = appData.description;
            newApplicant.LeadSource = 'Web';
            newApplicant.Status = 'Open - Not Contacted';

            insert newApplicant;
            return newApplicant.Id;

        } catch (AuraHandledException e) {
            throw e;
        } catch (Exception e) {
            throw new AuraHandledException('An unexpected error occurred: ' + e.getMessage());
        }
    }
}