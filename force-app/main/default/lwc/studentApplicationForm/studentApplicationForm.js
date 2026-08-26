import { LightningElement, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { createRecord } from 'lightning/uiRecordApi';
import CONTACT_OBJECT from '@salesforce/schema/Contact';
import FIRST_NAME_FIELD from '@salesforce/schema/Contact.FirstName';
import LAST_NAME_FIELD from '@salesforce/schema/Contact.LastName';
import EMAIL_FIELD from '@salesforce/schema/Contact.Email';
import PHONE_FIELD from '@salesforce/schema/Contact.Phone';
import TITLE_FIELD from '@salesforce/schema/Contact.Title';
import DESCRIPTION_FIELD from '@salesforce/schema/Contact.Description';

export default class StudentApplicationForm extends LightningElement {
    @track firstName = '';
    @track lastName = '';
    @track email = '';
    @track phone = '';
    @track programOfStudy = '';
    @track tuitionAmount = '';
    @track isLoading = false;

    get programOptions() {
        return [
            { label: 'Computer Science & Engineering', value: 'Computer Science' },
            { label: 'Business Administration', value: 'Business Administration' },
            { label: 'Data Science & AI', value: 'Data Science' },
            { label: 'Healthcare & Nursing', value: 'Healthcare' }
        ];
    }

    handleInputChange(event) {
        const field = event.target.name;
        if (field === 'firstName') {
            this.firstName = event.target.value;
        } else if (field === 'lastName') {
            this.lastName = event.target.value;
        } else if (field === 'email') {
            this.email = event.target.value;
        } else if (field === 'phone') {
            this.phone = event.target.value;
        } else if (field === 'programOfStudy') {
            this.programOfStudy = event.target.value;
        } else if (field === 'tuitionAmount') {
            this.tuitionAmount = event.target.value;
        }
    }

    validateInputs() {
        const allValid = [
            ...this.template.querySelectorAll('lightning-input, lightning-combobox')
        ].reduce((validSoFar, inputCmp) => {
            inputCmp.reportValidity();
            return validSoFar && inputCmp.checkValidity();
        }, true);

        return allValid;
    }

    async handleSubmit(event) {
        event.preventDefault();

        if (!this.validateInputs()) {
            this.showToast('Validation Error', 'Please complete all required fields properly.', 'error');
            return;
        }

        this.isLoading = true;

        const fields = {};
        fields[FIRST_NAME_FIELD.fieldApiName] = this.firstName;
        fields[LAST_NAME_FIELD.fieldApiName] = this.lastName;
        fields[EMAIL_FIELD.fieldApiName] = this.email;
        fields[PHONE_FIELD.fieldApiName] = this.phone;
        fields[TITLE_FIELD.fieldApiName] = `Student - ${this.programOfStudy}`;
        fields[DESCRIPTION_FIELD.fieldApiName] = `Tuition Amount: $${this.tuitionAmount} | Program: ${this.programOfStudy}`;

        const recordInput = { apiName: CONTACT_OBJECT.objectApiName, fields };

        try {
            const contact = await createRecord(recordInput);
            this.showToast(
                'Success',
                `Student registration successful! Reference ID: ${contact.id}`,
                'success'
            );
            this.handleReset();
        } catch (error) {
            let message = 'An error occurred while creating the record.';
            if (error.body && error.body.message) {
                message = error.body.message;
            }
            this.showToast('Error Registering Student', message, 'error');
        } finally {
            this.isLoading = false;
        }
    }

    handleReset() {
        this.firstName = '';
        this.lastName = '';
        this.email = '';
        this.phone = '';
        this.programOfStudy = '';
        this.tuitionAmount = '';

        const inputFields = this.template.querySelectorAll('lightning-input, lightning-combobox');
        if (inputFields) {
            inputFields.forEach(field => {
                field.value = '';
                if (typeof field.setCustomValidity === 'function') {
                    field.setCustomValidity('');
                    field.reportValidity();
                }
            });
        }
    }

    showToast(title, message, variant) {
        const evt = new ShowToastEvent({
            title: title,
            message: message,
            variant: variant
        });
        this.dispatchEvent(evt);
    }
}