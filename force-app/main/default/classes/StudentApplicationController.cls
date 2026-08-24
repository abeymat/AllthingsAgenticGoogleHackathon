public with sharing class StudentApplicationController {

    public class ApplicationDTO {
        @AuraEnabled public String firstName { get; set; }
        @AuraEnabled public String lastName { get; set; }
        @AuraEnabled public String email { get; set; }
        @AuraEnabled public String phone { get; set; }
        @AuraEnabled public String institutionName { get; set; }
        @AuraEnabled public String programOfInterest { get; set; }
        @AuraEnabled public String notes { get; set; }
    }

    /**
     * Submits a new student application represented as a Lead record.
     * Uses standard Lead schema to ensure Developer Edition and org portability.
     * 
     * @param appData The application payload captured from the UI.
     * @return Id The Id of the created Lead record.
     */
    @AuraEnabled
    public static Id submitApplication(ApplicationDTO appData) {
        if (appData == null) {
            throw new AuraHandledException('Application data cannot be empty.');
        }

        if (String.isBlank(appData.lastName)) {
            throw new AuraHandledException('Last Name is a required field.');
        }

        try {
            Lead newApplication = new Lead();
            newApplication.FirstName = appData.firstName;
            newApplication.LastName = appData.lastName;
            newApplication.Email = appData.email;
            newApplication.Phone = appData.phone;
            newApplication.Company = String.isNotBlank(appData.institutionName) 
                ? appData.institutionName 
                : 'Prospective Student';
            newApplication.LeadSource = 'Web Application';
            
            String descriptionDetails = '';
            if (String.isNotBlank(appData.programOfInterest)) {
                descriptionDetails += 'Program of Interest: ' + appData.programOfInterest + '\n';
            }
            if (String.isNotBlank(appData.notes)) {
                descriptionDetails += 'Notes: ' + appData.notes;
            }
            newApplication.Description = descriptionDetails.trim();

            SObjectAccessDecision decision = Security.stripInaccessible(
                AccessType.CREATABLE, 
                new List<Lead>{ newApplication }
            );

            List<Lead> sanitizedRecords = decision.getRecords();
            insert sanitizedRecords;

            return sanitizedRecords[0].Id;
        } catch (Exception ex) {
            throw new AuraHandledException('Error submitting application: ' + ex.getMessage());
        }
    }
}