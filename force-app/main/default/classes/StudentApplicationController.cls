public with sharing class StudentApplicationController {

    public class ApplicationException extends Exception {}

    /**
     * Submits a student application by creating a Lead record.
     * Uses standard fields for standard developer edition compatibility.
     * 
     * @param applicantData Map containing applicant attributes (firstName, lastName, email, phone, company/program)
     * @return Id of the created application (Lead) record
     */
    @AuraEnabled
    public static Id submitApplication(Map<String, String> applicantData) {
        try {
            if (applicantData == null || applicantData.isEmpty()) {
                throw new ApplicationException('Applicant data cannot be null or empty.');
            }

            String firstName = applicantData.get('firstName');
            String lastName = applicantData.get('lastName');
            String email = applicantData.get('email');
            String phone = applicantData.get('phone');
            String program = applicantData.get('program');

            if (String.isBlank(lastName)) {
                throw new ApplicationException('Last Name is a required field.');
            }

            Lead studentLead = new Lead(
                FirstName = firstName,
                LastName = lastName,
                Email = email,
                Phone = phone,
                Company = String.isBlank(program) ? 'Student Application' : program,
                Status = 'Open - Not Contacted',
                LeadSource = 'Web'
            );

            insert as user studentLead;

            return studentLead.Id;

        } catch (Exception e) {
            AuraHandledException auraEx = new AuraHandledException(e.getMessage());
            auraEx.setMessage(e.getMessage());
            throw auraEx;
        }
    }

    /**
     * Bulk submits student applications.
     * 
     * @param applicationsList List of maps containing student data
     * @return List of created Lead IDs
     */
    @AuraEnabled
    public static List<Id> submitBulkApplications(List<Map<String, String>> applicationsList) {
        try {
            if (applicationsList == null || applicationsList.isEmpty()) {
                throw new ApplicationException('Application list cannot be null or empty.');
            }

            List<Lead> leadsToInsert = new List<Lead>();

            for (Map<String, String> applicantData : applicationsList) {
                String firstName = applicantData.get('firstName');
                String lastName = applicantData.get('lastName');
                String email = applicantData.get('email');
                String phone = applicantData.get('phone');
                String program = applicantData.get('program');

                if (String.isNotBlank(lastName)) {
                    leadsToInsert.add(new Lead(
                        FirstName = firstName,
                        LastName = lastName,
                        Email = email,
                        Phone = phone,
                        Company = String.isBlank(program) ? 'Student Application' : program,
                        Status = 'Open - Not Contacted',
                        LeadSource = 'Web'
                    ));
                }
            }

            if (!leadsToInsert.isEmpty()) {
                insert as user leadsToInsert;
            }

            List<Id> insertedIds = new List<Id>();
            for (Lead leadRecord : leadsToInsert) {
                insertedIds.add(leadRecord.Id);
            }

            return insertedIds;

        } catch (Exception e) {
            AuraHandledException auraEx = new AuraHandledException(e.getMessage());
            auraEx.setMessage(e.getMessage());
            throw auraEx;
        }
    }
}