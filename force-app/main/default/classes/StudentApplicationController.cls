public with sharing class StudentApplicationController {

    public class ApplicationWrapper {
        @AuraEnabled public String firstName { get; set; }
        @AuraEnabled public String lastName { get; set; }
        @AuraEnabled public String email { get; set; }
        @AuraEnabled public String phone { get; set; }
        @AuraEnabled public String company { get; set; }
        @AuraEnabled public Decimal tuitionAmount { get; set; }
    }

    @AuraEnabled
    public static Map<String, Object> submitApplication(ApplicationWrapper appData) {
        Map<String, Object> response = new Map<String, Object>();
        
        if (appData == null || String.isBlank(appData.lastName) || String.isBlank(appData.email)) {
            throw new AuraHandledException('Last Name and Email are required parameters.');
        }

        try {
            List<Contact> existingContacts = [
                SELECT Id, FirstName, LastName, Email, Phone 
                FROM Contact 
                WHERE Email = :appData.email 
                WITH USER_MODE
                LIMIT 1
            ];

            Contact studentContact;
            if (!existingContacts.isEmpty()) {
                studentContact = existingContacts[0];
                studentContact.FirstName = appData.firstName;
                studentContact.Phone = appData.phone;
                update studentContact;
            } else {
                studentContact = new Contact(
                    FirstName = appData.firstName,
                    LastName = appData.lastName,
                    Email = appData.email,
                    Phone = appData.phone
                );
                insert studentContact;
            }

            Opportunity tuitionOpp = new Opportunity(
                Name = appData.lastName + ' - Tuition Application',
                StageName = 'Prospecting',
                CloseDate = System.today().addDays(30),
                Amount = appData.tuitionAmount,
                ContactId = studentContact.Id
            );
            insert tuitionOpp;

            response.put('status', 'SUCCESS');
            response.put('contactId', studentContact.Id);
            response.put('opportunityId', tuitionOpp.Id);
            response.put('message', 'Application submitted successfully.');
        } catch (Exception ex) {
            throw new AuraHandledException('Failed to submit application: ' + ex.getMessage());
        }

        return response;
    }

    @AuraEnabled(cacheable=true)
    public static List<Opportunity> getStudentTuitionApplications(String email) {
        if (String.isBlank(email)) {
            return new List<Opportunity>();
        }

        return [
            SELECT Id, Name, StageName, Amount, CloseDate, Contact.Name, Contact.Email
            FROM Opportunity
            WHERE Contact.Email = :email
            WITH USER_MODE
            ORDER BY CreatedDate DESC
        ];
    }
}