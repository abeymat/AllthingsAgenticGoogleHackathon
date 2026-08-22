import { LightningElement, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { createRecord } from 'lightning/uiRecordApi';
import LEAD_OBJECT from '@salesforce/schema/Lead';
import FIRST_NAME_FIELD from '@salesforce/schema/Lead.FirstName';
import LAST_NAME_FIELD from '@salesforce/schema/Lead.LastName';
import EMAIL_FIELD from '@salesforce/schema/Lead.Email';
import PHONE_FIELD from '@salesforce/schema/Lead.Phone';
import COMPANY_FIELD from '@salesforce/schema/Lead.Company';

export default class StudentApplicationForm extends LightningElement {
    @track firstName = '';
    @track lastName = '';
    @track email = '';
    @track phone = '';
    @track company = '';

    isLoading = false;

    handleInputChange(event) {
        const fieldName = event.target.dataset.id;
        if (fieldName === 'firstName') {
            this.firstName = event.target.value;
        } else if (fieldName === 'lastName') {
            this.lastName = event.target.value;
        } else if (fieldName === 'email') {
            this.email = event.target.value;
        } else if (fieldName === 'phone') {
            this.phone = event.target.value;
        } else if (fieldName === 'company') {
            this.company = event.target.value;
        }
    }

    validateInputs() {
        const allValid = [
            ...this.template.querySelectorAll('lightning-input')
        ].reduce((validSoFar, inputFields) => {
            inputFields.reportValidity();
            return validSoFar && inputFields.checkValidity();
        }, true);

        return allValid;
    }

    async handleSubmit() {
        if (!this.validateInputs()) {
            this.showToast('Validation Error', 'Please complete all required fields.', 'error');
            return;
        }

        this.isLoading = true;

        const fields = {};
        fields[FIRST_NAME_FIELD.fieldApiName] = this.firstName;
        fields[LAST_NAME_FIELD.fieldApiName] = this.lastName;
        fields[EMAIL_FIELD.fieldApiName] = this.email;
        fields[PHONE_FIELD.fieldApiName] = this.phone;
        fields[COMPANY_FIELD.fieldApiName] = this.company || 'Student Application';

        const recordInput = { apiName: LEAD_OBJECT.objectApiName, fields };

        try {
            const leadRecord = await createRecord(recordInput);
            this.showToast('Success', `Application submitted successfully! Application ID: ${leadRecord.id}`, 'success');
            this.resetForm();
        } catch (error) {
            let errorMessage = 'An error occurred while submitting the application.';
            if (error && error.body && error.body.message) {
                errorMessage = error.body.message;
            }
            this.showToast('Error Creating Record', errorMessage, 'error');
        } finally {
            this.isLoading = false;
        }
    }

    resetForm() {
        this.firstName = '';
        this.lastName = '';
        this.email = '';
        this.phone = '';
        this.company = '';
        
        const inputFields = this.template.querySelectorAll('lightning-input');
        if (inputFields) {
            inputFields.forEach(field => {
                field.value = '';
            });
        }
    }

    showToast(title, message, variant) {
        const event = new ShowToastEvent({
            title: title,
            message: message,
            variant: variant
        });
        this.dispatchEvent(event);
    }
}